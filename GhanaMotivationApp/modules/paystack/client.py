"""Async Paystack HTTP client with mock mode support.

This module provides a single async client class that abstracts
Paystack's REST API. When PAYSTACK_MODE='mock', it returns fake
responses without making network calls.
"""



import uuid
import httpx

from GhanaMotivationApp.settings import settings
from .schema import (
    PaystackInitRequest,
    PaystackInitResponse,
    PaystackInitResponseData,
    PaystackVerifyResponse,
    PaystackVerifyResponseData
)


class PaystackClient:


    def __init__(self):
        self.base_url = settings.PAYSTACK_BASE_URL
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.is_mock = settings.PAYSTACK_MODE == 'mock'



    def _headers(self) -> dict[str, str]:
        """Builds the Authorization header for Paystack API calls."""
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    async def initialize_transaction(
        self, request: PaystackInitRequest
    ) -> PaystackInitResponse:
        """Initializes a Paystack transaction.

        Args:
            request: The transaction initialization data.

        Returns:
            PaystackInitResponse with authorization_url and reference.
        """
        if self.is_mock:
            ref = f"MOCK-{uuid.uuid4().hex[:12].upper()}"
            return PaystackInitResponse(
                status=True,
                message="Authorization URL created.",
                data= PaystackInitResponseData(
                    authorization_url=f"https://checkout.paystack.com/mock/{ref}",
                    access_code=ref,
                    reference=ref
                )
            )

    # Live mode — real HTTP call
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/transaction/initialize",
                headers=self._headers(),
                json=request.model_dump(),
            )
            response.raise_for_status()
            return PaystackInitResponse.model_validate(response.json())

    async def verify_transaction(self, reference: str) -> PaystackVerifyResponse:
        """Verifies a Paystack transaction by its reference.

        Args:
            reference: The unique transaction reference string.

        Returns:
            PaystackVerifyResponse with transaction status and details.
        """
        if self.is_mock:
            return PaystackVerifyResponse(
                status=True,
                message="Verification successful",
                data=PaystackVerifyResponseData(
                    status="success",
                    reference=reference,
                    amount=settings.SUBSCRIPTION_AMOUNT_PESEWAS,
                    currency="GHS",
                    paid_at="2026-08-28T00:00:00.000Z",
                    customer={"email": "mock@example.com"},
                ),
            )

        # Live mode
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/transaction/verify/{reference}",
                headers=self._headers(),
            )
            response.raise_for_status()
            return PaystackVerifyResponse.model_validate(response.json())