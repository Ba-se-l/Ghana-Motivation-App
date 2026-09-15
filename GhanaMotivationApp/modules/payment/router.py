"""Payment domain router.

Provides endpoints for Paystack payment initialization,
transaction verification, and webhook handling.
"""

from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.settings import settings
from GhanaMotivationApp.database import get_session
from GhanaMotivationApp.modules.auth.dependencies import get_current_user
from GhanaMotivationApp.modules.user import User
from .schema import PaymentInitResponse, PaymentResponse
from .exceptions import InvalidWebhookSignatureException
from . import service

router = APIRouter(prefix=f"{settings.API_PREFIX}/payments", tags=["Payments"])


@router.post(
    "/initialize",
    response_model=PaymentInitResponse,
    status_code=status.HTTP_200_OK,
    summary="Initialize Paystack subscription payment",
)
async def initialize_subscription(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> PaymentInitResponse:
    """Starts a Paystack transaction using server-derived identity and price."""
    return await service.initialize_payment(
        user_id=current_user.id,
        email=current_user.email,
        session=session,
    )


@router.get(
    "/verify",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify a Paystack transaction",
)
async def verify_transaction(
    reference: str = Query(..., description="Paystack transaction reference"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> PaymentResponse:
    """Verifies a transaction with Paystack and activates premium if successful."""
    payment = await service.verify_and_activate(
        reference=reference,
        session=session,
        requesting_user_id=current_user.id,
    )
    return PaymentResponse.model_validate(payment)


@router.post(
    "/webhook",
    status_code=status.HTTP_200_OK,
    summary="Paystack webhook receiver",
)
async def webhook(
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Receives and processes Paystack webhook events (e.g., charge.success).

    Always returns 200 OK to prevent Paystack retries, even for
    already-processed events or unsupported event types.
    """
    import json

    # Step 1: Verify HMAC signature
    signature = request.headers.get("X-Paystack-Signature", "")
    body = await request.body()

    if not service.verify_webhook_signature(payload_body=body, signature=signature):
        raise InvalidWebhookSignatureException()

    # Step 2: Parse event with controlled error handling
    try:
        event = json.loads(body)
    except (json.JSONDecodeError, ValueError):
        return {"status": "invalid_payload"}

    event_type = event.get("event", "")

    # Step 3: Process charge.success only
    if event_type == "charge.success":
        reference = event.get("data", {}).get("reference")
        if reference:
            await service.webhook_verify_and_activate(
                reference=reference,
                session=session,
            )

    return {"status": "ok"}