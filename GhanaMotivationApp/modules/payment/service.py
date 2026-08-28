"""Payment domain service layer.

Orchestrates payment initialization, Paystack verification,
and webhook processing. Delegates to PaystackClient for
external API calls and to repositories for persistence.
"""

import hashlib
import hmac
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.settings import settings
from GhanaMotivationApp.modules.paystack import PaystackClient, PaystackInitRequest
from GhanaMotivationApp.modules.user import UserRepository, UserNotFoundException
from GhanaMotivationApp.modules.subscription.repo import SubscriptionRepository
from GhanaMotivationApp.modules.subscription.model import Subscription
from .model import Payment
from .repo import PaymentRepository
from .exceptions import DuplicatePaymentException, PaymentVerificationFailedException, InvalidWebhookSignatureException
from GhanaMotivationApp.modules.payment.schema import InitSubscriptionRequest, PaymentInitResponse


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

    now = datetime.now(timezone.utc)

    # Renewal Extension Logic:
    # If premium_expires exists and is in the future, extend from it
    if user.premium_expires and user.premium_expires > now:
        start_date = user.premium_expires
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
        active=True,
    )
    await sub_repo.create(orm_model=subscription)

async def initialize_payment(
    schema: InitSubscriptionRequest, session: AsyncSession
) -> PaymentInitResponse:
    """Initializes a payment transaction with Paystack.

    Orchestration:
        1. Call Paystack to initialize transaction.
        2. Create a pending Payment record in the database.
        3. Return the authorization URL to the client.

    Args:
        schema: Contains user_id, email, amount.
        session: The active database session.

    Returns:
        PaymentInitResponse with authorization_url and reference.
    """
    paystack_client = PaystackClient()

    # Step 1: Initialize with Paystack
    paystack_response = await paystack_client.initialize_transaction(
        PaystackInitRequest(
            email=schema.email,
            amount=schema.amount,
        )
    )

    reference = paystack_response.data.reference

    # Step 2: Create pending payment record
    payment_repo = PaymentRepository(session=session)
    payment = Payment(
        reference=reference,
        amount=schema.amount,
        currency="GHS",
        status="pending",
        user_id=schema.user_id,
    )
    await payment_repo.create(orm_model=payment)

    # Step 3: Return URL
    return PaymentInitResponse(
        authorization_url=paystack_response.data.authorization_url,
        reference=reference,
    )



async def verify_and_activate(reference: str, session: AsyncSession) -> Payment:
    """Verifies a Paystack transaction and activates premium if successful.

    Orchestration:
        1. Check if payment already processed (idempotency).
        2. Verify with Paystack API.
        3. Update payment record status.
        4. If successful: activate premium subscription.

    Args:
        reference: The Paystack transaction reference.
        session: The active database session.

    Returns:
        The updated Payment record.

    Raises:
        DuplicatePaymentException: If reference already has status 'success'.
        PaymentVerificationFailedException: If Paystack reports non-success.
    """
    payment_repo = PaymentRepository(session=session)
    paystack_client = PaystackClient()

    # Step 1: Check for existing processed payment (idempotency)
    existing = await payment_repo.get_by_reference(reference)
    if existing and existing.status == "success":
        raise DuplicatePaymentException(reference=reference)

    # Step 2: Verify with Paystack
    verify_response = await paystack_client.verify_transaction(reference)
    paystack_status = verify_response.data.status

    # Step 3: Update or create payment record
    if existing:
        await payment_repo.update(
            orm_model=existing,
            update_data={
                'status': paystack_status,
                'paid_at': datetime.now(timezone.utc) if paystack_status == "success" else None,
            },
        )
        payment = existing
    else:
        payment = Payment(
            reference=reference,
            amount=verify_response.data.amount,
            currency=verify_response.data.currency,
            status=paystack_status,
            paid_at=datetime.now(timezone.utc) if paystack_status == "success" else None,
            user_id=0,  # Will be resolved from Paystack customer email
        )
        await payment_repo.create(orm_model=payment)

    # Step 4: If successful — activate premium
    if paystack_status == "success" and existing:
        await _activate_premium_for_user(
            user_id=existing.user_id, session=session
        )

    if paystack_status != "success":
        raise PaymentVerificationFailedException(
            reference=reference, paystack_status=paystack_status
        )

    return payment


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