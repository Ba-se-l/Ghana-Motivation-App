"""Payment domain router.

Provides endpoints for Paystack payment initialization,
transaction verification, and webhook handling.
"""

from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.settings import settings
from GhanaMotivationApp.database import get_session
from .schema import InitSubscriptionRequest, PaymentInitResponse, VerifyTransactionResponse, PaymentResponse
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
    request: InitSubscriptionRequest,
    session: AsyncSession = Depends(get_session),
) -> PaymentInitResponse:
    """Starts a Paystack transaction and returns the checkout URL."""
    return await service.initialize_payment(schema=request, session=session)


@router.get(
    "/verify",
    response_model=PaymentResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify a Paystack transaction",
)
async def verify_transaction(
    reference: str = Query(..., description="Paystack transaction reference"),
    session: AsyncSession = Depends(get_session),
) -> PaymentResponse:
    """Verifies a transaction with Paystack and activates premium if successful."""
    payment = await service.verify_and_activate(reference=reference, session=session)
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
    """Receives and processes Paystack webhook events (e.g., charge.success)."""
    # Step 1: Verify HMAC signature
    signature = request.headers.get("X-Paystack-Signature", "")
    body = await request.body()

    if not service.verify_webhook_signature(payload_body=body, signature=signature):
        raise InvalidWebhookSignatureException()

    # Step 2: Parse event
    import json
    event = json.loads(body)
    event_type = event.get("event", "")

    # Step 3: Process charge.success
    if event_type == "charge.success":
        reference = event["data"]["reference"]
        await service.verify_and_activate(reference=reference, session=session)

    return {"status": "ok"}