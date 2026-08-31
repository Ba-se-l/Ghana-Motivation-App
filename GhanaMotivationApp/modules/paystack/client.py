"""Async Paystack HTTP client with mock mode support.

This module provides a single async client class that abstracts Paystack's
REST API. When PAYSTACK_MODE='mock', it returns fake responses without making
external network requests.
"""

import uuid
from datetime import datetime, timezone
import httpx

from GhanaMotivationApp.core import CurrencyEnum, PaymentStatusEnum
from GhanaMotivationApp.settings import settings
from .schema import (
    PaystackInitRequest,
    PaystackInitResponse,
    PaystackInitResponseData,
    PaystackVerifyResponse,
    PaystackVerifyResponseData,
)


class PaystackClient:
    """Async HTTP client wrapper for Paystack REST API transactions.

    Attributes:
        base_url: Base URL string for Paystack API requests.
        secret_key: Secret key string for HTTP bearer authorization.
        is_mock: Boolean flag enabling mock responses for development.
    """

    def __init__(self) -> None:
        """Initializes the Paystack client using settings configuration."""
        self.base_url = settings.PAYSTACK_BASE_URL
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.is_mock = settings.PAYSTACK_MODE == 'mock'

    def _headers(self) -> dict[str, str]:
        """Builds default HTTP authorization and header metadata.

        Returns:
            Dictionary containing Authorization bearer token and Content-Type.
        """
        return {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    async def initialize_transaction(
        self, request: PaystackInitRequest
    ) -> PaystackInitResponse:
        """Initializes a subscription payment transaction with Paystack.

        Args:
            request: The transaction initialization request parameters.

        Returns:
            `PaystackInitResponse` object with authorization_url and reference.

        Raises:
            httpx.HTTPStatusError: If live API returns non-2xx response.
        """
        if self.is_mock:
            # Generate mock reference code
            ref = f"MOCK-{uuid.uuid4().hex[:12].upper()}"
            return PaystackInitResponse(
                status=True,
                message="Authorization URL created.",
                data=PaystackInitResponseData(
                    authorization_url=f"https://checkout.paystack.com/mock/{ref}",
                    access_code=ref,
                    reference=ref,
                ),
            )

        # Live mode — real HTTP request to Paystack REST API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/transaction/initialize",
                headers=self._headers(),
                json=request.model_dump(),
            )
            response.raise_for_status()
            return PaystackInitResponse.model_validate(response.json())

    async def verify_transaction(
        self, reference: str, customer_email: str = 'mock-verified@test.com'
    ) -> PaystackVerifyResponse:
        """Verifies a transaction using its unique reference identifier.

        Args:
            reference: The unique transaction reference string.
            customer_email: Optional email to include in mock response data.

        Returns:
            `PaystackVerifyResponse` object containing transaction status and details.

        Raises:
            httpx.HTTPStatusError: If live API returns non-2xx response.
        """
        if self.is_mock:
            # Return dynamic mock response with current UTC timestamp
            return PaystackVerifyResponse(
                status=True,
                message="Verification successful",
                data=PaystackVerifyResponseData(
                    status=PaymentStatusEnum.SUCCESS.value,
                    reference=reference,
                    amount=settings.SUBSCRIPTION_AMOUNT_PESEWAS,
                    currency=CurrencyEnum.GHANA,
                    paid_at=datetime.now(timezone.utc).isoformat(),
                    customer={"email": customer_email},
                ),
            )

        # Live mode — real HTTP request to Paystack verification endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/transaction/verify/{reference}",
                headers=self._headers(),
            )
            response.raise_for_status()
            return PaystackVerifyResponse.model_validate(response.json())