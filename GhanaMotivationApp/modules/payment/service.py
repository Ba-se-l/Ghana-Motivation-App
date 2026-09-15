"""Payment domain service layer.

Orchestrates payment initialization, Paystack verification,
and webhook processing. Delegates to PaystackClient for
external API calls and to repositories for persistence.
"""

import hashlib
import hmac
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.core import (
    CurrencyEnum,
    PaymentStatusEnum,
    SubscriptionStatusEnum,
    PaymentAmountMismatchException,
    PaymentCurrencyMismatchException,
    PaymentOwnershipException,
)
from GhanaMotivationApp.settings import settings
from GhanaMotivationApp.modules.paystack import PaystackClient, PaystackInitRequest
from GhanaMotivationApp.modules.user import UserRepository, UserNotFoundException
from GhanaMotivationApp.modules.subscription.repo import SubscriptionRepository
from GhanaMotivationApp.modules.subscription.model import Subscription
from .model import Payment
from .repo import PaymentRepository
from .exceptions import DuplicatePaymentException, PaymentVerificationFailedException
from .schema import PaymentInitResponse

logger = logging.getLogger(__name__)


async def _activate_premium_for_user(user_id: int, session: AsyncSession) -> None:
    """Activates or extends premium for a user.

    Business Rule (Renewal Extension):
        If the user already has an active premium that hasn't expired yet,
        the new 30-day period starts from the EXISTING expiration date,
        not from today. This prevents the user from losing remaining days.

    Args:
        user_id: The user's primary key.
        session: The active database session.
    """
    user_repo = UserRepository(session=session)
    sub_repo = SubscriptionRepository(session=session)

    user = await user_repo.get_by_id(id=user_id)
    if user is None:
        raise UserNotFoundException(identifier=str(user_id))

    # Deactivate any existing active subscriptions for this user
    await sub_repo.deactivate_all_for_user(user_id=user_id)

    now = datetime.now(timezone.utc)

    # Renewal Extension Logic:
    # If premium_expires exists and is in the future, extend from it
    if user.premium_expires:
        prem_exp = user.premium_expires
        if prem_exp.tzinfo is None:
            prem_exp = prem_exp.replace(tzinfo=timezone.utc)
        if prem_exp > now:
            start_date = prem_exp
        else:
            start_date = now
    else:
        start_date = now

    new_expiry = start_date + timedelta(days=settings.SUBSCRIPTION_DAYS)

    # Update user premium status
    await user_repo.update(
        orm_model=user,
        update_data={
            'is_premium': True,
            'premium_expires': new_expiry,
        },
    )

    # Create subscription record
    subscription = Subscription(
        user_id=user_id,
        start_date=start_date,
        next_billing=new_expiry,
        status=SubscriptionStatusEnum.ACTIVE.value,
    )
    await sub_repo.create(orm_model=subscription)

async def initialize_payment(
    user_id: int, email: str, session: AsyncSession
) -> PaymentInitResponse:
    """Initializes a payment transaction with server-derived identity and price.

    The amount and currency are resolved from server settings, NOT from
    client input. The user identity comes from the authenticated JWT.

    Orchestration:
        1. Call Paystack to initialize transaction with server price.
        2. Create a pending Payment record in the database.
        3. Return the authorization URL to the client.

    Args:
        user_id: The authenticated user's primary key (from JWT).
        email: The authenticated user's email (from JWT).
        session: The active database session.

    Returns:
        PaymentInitResponse with authorization_url and reference.
    """
    paystack_client = PaystackClient()
    server_amount = settings.SUBSCRIPTION_AMOUNT_PESEWAS

    # Step 1: Initialize with Paystack using SERVER-defined price
    paystack_response = await paystack_client.initialize_transaction(
        PaystackInitRequest(
            email=email,
            amount=server_amount,
        )
    )

    reference = paystack_response.data.reference

    # Step 2: Create pending payment record
    payment_repo = PaymentRepository(session=session)
    payment = Payment(
        reference=reference,
        amount=server_amount,
        currency=CurrencyEnum.GHANA,
        status=PaymentStatusEnum.PENDING.value,
        user_id=user_id,
    )
    await payment_repo.create(orm_model=payment)
    await session.flush()

    # Step 3: Return URL
    return PaymentInitResponse(
        authorization_url=paystack_response.data.authorization_url,
        reference=reference,
    )


async def verify_and_activate(
    reference: str,
    session: AsyncSession,
    requesting_user_id: int,
) -> Payment:
    """Verifies a Paystack transaction with full trust-boundary validation.

    Orchestration:
        1. Check if payment already processed (return if so — idempotent).
        2. Verify ownership: payment must belong to requesting user.
        3. Verify with Paystack API.
        4. Validate amount and currency match server expectations.
        5. Atomically transition payment status to success.
        6. If successful: activate premium subscription.

    Args:
        reference: The Paystack transaction reference.
        session: The active database session.
        requesting_user_id: The authenticated user's ID (from JWT).

    Returns:
        The updated Payment record.

    Raises:
        PaymentOwnershipException: If reference doesn't belong to requesting user.
        PaymentAmountMismatchException: If verified amount != expected price.
        PaymentCurrencyMismatchException: If verified currency != expected currency.
        PaymentVerificationFailedException: If Paystack reports non-success.
    """
    payment_repo = PaymentRepository(session=session)
    paystack_client = PaystackClient()

    # Step 1: Check for existing processed payment (idempotency)
    existing = await payment_repo.get_by_reference(reference)

    if existing and existing.status == PaymentStatusEnum.SUCCESS.value:
        # Already processed — return silently (idempotent)
        return existing

    # Step 2: Verify ownership
    if existing and existing.user_id != requesting_user_id:
        raise PaymentOwnershipException(reference=reference)

    # Step 3: Verify with Paystack
    verify_response = await paystack_client.verify_transaction(reference)
    paystack_status = verify_response.data.status

    # Step 4: Validate amount and currency
    if paystack_status == PaymentStatusEnum.SUCCESS.value:
        expected_amount = settings.SUBSCRIPTION_AMOUNT_PESEWAS
        expected_currency = settings.SUBSCRIPTION_CURRENCY

        if verify_response.data.amount != expected_amount:
            raise PaymentAmountMismatchException(
                expected=expected_amount,
                actual=verify_response.data.amount,
                currency=expected_currency,
            )

        if verify_response.data.currency != expected_currency:
            raise PaymentCurrencyMismatchException(
                expected=expected_currency,
                actual=verify_response.data.currency,
            )

    # Step 5: Atomically update payment status
    if existing:
        updated = await payment_repo.atomic_mark_success(
            payment_id=existing.id,
            new_status=paystack_status,
        )
        if not updated and paystack_status == PaymentStatusEnum.SUCCESS.value:
            # Another request already processed this — idempotent
            refreshed = await payment_repo.get_by_reference(reference)
            if refreshed is not None:
                return refreshed
            return existing

        await session.refresh(existing)
        payment = existing
        payment.status = paystack_status
        if paystack_status == PaymentStatusEnum.SUCCESS.value and payment.paid_at is None:
            payment.paid_at = datetime.now(timezone.utc)
    else:
        # No local record — should not happen in normal flow
        logger.warning(
            "verify_and_activate called for unknown reference=%s by user=%s",
            reference,
            requesting_user_id,
        )
        raise PaymentVerificationFailedException(
            reference=reference, paystack_status="UNKNOWN_REFERENCE"
        )

    # Step 6: If successful — activate premium
    if paystack_status == PaymentStatusEnum.SUCCESS.value:
        await _activate_premium_for_user(
            user_id=payment.user_id, session=session
        )

    if paystack_status != PaymentStatusEnum.SUCCESS.value:
        raise PaymentVerificationFailedException(
            reference=reference, paystack_status=paystack_status
        )

    return payment


async def webhook_verify_and_activate(
    reference: str,
    session: AsyncSession,
) -> None:
    """Webhook-specific payment verification — always idempotent.

    Unlike the client-facing verify_and_activate, this function:
    - Does NOT raise on duplicate payments (returns silently).
    - Does NOT require a requesting_user_id (authenticated by HMAC signature).
    - Logs warnings instead of raising on validation failures.

    Args:
        reference: The Paystack transaction reference from the webhook event.
        session: The active database session.
    """
    payment_repo = PaymentRepository(session=session)
    paystack_client = PaystackClient()

    # Step 1: Check if already processed
    existing = await payment_repo.get_by_reference(reference)
    if existing and existing.status == PaymentStatusEnum.SUCCESS.value:
        logger.info("Webhook: reference=%s already processed. Ignoring.", reference)
        return

    # Step 2: Verify with Paystack
    try:
        verify_response = await paystack_client.verify_transaction(reference)
    except Exception:
        logger.exception("Webhook: Paystack verification failed for reference=%s", reference)
        return

    paystack_status = verify_response.data.status

    if paystack_status != PaymentStatusEnum.SUCCESS.value:
        logger.info(
            "Webhook: reference=%s has status=%s. Skipping activation.",
            reference,
            paystack_status,
        )
        if existing:
            await payment_repo.update(
                orm_model=existing,
                update_data={'status': paystack_status},
            )
        return

    # Step 3: Validate amount and currency
    expected_amount = settings.SUBSCRIPTION_AMOUNT_PESEWAS
    expected_currency = settings.SUBSCRIPTION_CURRENCY

    if verify_response.data.amount != expected_amount:
        logger.error(
            "Webhook: Amount mismatch for reference=%s. Expected=%d, Got=%d",
            reference,
            expected_amount,
            verify_response.data.amount,
        )
        return

    if verify_response.data.currency != expected_currency:
        logger.error(
            "Webhook: Currency mismatch for reference=%s. Expected=%s, Got=%s",
            reference,
            expected_currency,
            verify_response.data.currency,
        )
        return

    # Step 4: Atomically update payment
    if existing:
        updated = await payment_repo.atomic_mark_success(
            payment_id=existing.id,
            new_status=PaymentStatusEnum.SUCCESS.value,
        )
        if not updated:
            logger.info("Webhook: reference=%s already transitioned. Ignoring.", reference)
            return

        # Step 5: Activate premium
        await _activate_premium_for_user(
            user_id=existing.user_id, session=session
        )
        logger.info(
            "Webhook: Premium activated for user=%d via reference=%s",
            existing.user_id,
            reference,
        )
    else:
        logger.warning("Webhook: No local payment found for reference=%s", reference)


def verify_webhook_signature(payload_body: bytes, signature: str) -> bool:
    """Verifies Paystack webhook HMAC SHA-512 signature.

    Args:
        payload_body: The raw request body bytes.
        signature: The value of X-Paystack-Signature header.

    Returns:
        True if the signature is valid.
    """
    expected = hmac.new(
        key=settings.PAYSTACK_SECRET_KEY.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha512,
    ).hexdigest()

    return hmac.compare_digest(expected, signature)