"""Payment domain Pydantic validation schemas.

Defines data structures for transaction initialization, Paystack responses,
and serialized payment entity records returned by API endpoints.
"""

from datetime import datetime
from pydantic import BaseModel as Base, ConfigDict, Field, field_serializer

from GhanaMotivationApp.core import CurrencyEnum


class _C(Base):
    """Base schema configuration allowing ORM model attribute mapping."""

    model_config = ConfigDict(from_attributes=True)


class InitSubscriptionRequest(Base):
    """Request payload for initializing a new subscription payment."""

    user_id: int = Field(...)
    """Unique integer identifier of the paying user."""

    email: str = Field(..., min_length=5, max_length=100, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    """Email address associated with the Paystack transaction."""

    amount: int = Field(..., gt=0, description="Amount in pesewas (minor units: 1000 = 10 GHS)")
    """Total payment amount specified in Ghanaian Pesewas."""


class PaymentInitResponse(Base):
    """Response payload containing Paystack checkout authorization details."""

    authorization_url: str
    """Web URL redirecting the user to Paystack's payment checkout gateway."""

    reference: str
    """Unique Paystack transaction reference string."""


class VerifyTransactionResponse(Base):
    """Passthrough response structure from Paystack verification endpoint."""

    status: str
    """Verification operation status string."""

    message: str
    """Human-readable message from Paystack."""

    data: dict
    """Raw verification payload dictionary."""


class PaymentResponse(_C):
    """Serialized payment entity returned by payment API endpoints."""

    id: int
    """Unique integer identifier of the payment record."""

    reference: str
    """Unique Paystack transaction reference string."""

    amount: int
    """Payment amount in Ghanaian Pesewas."""

    currency: CurrencyEnum
    """Currency unit enumeration identifier (GHS)."""

    status: str
    """Transaction state progression status (e.g. pending, success)."""

    paid_at: datetime | None
    """UTC timestamp when the transaction was completed."""

    user_id: int
    """Foreign key user identifier."""

    created_at: datetime
    """Record creation UTC timestamp."""

    updated_at: datetime
    """Record last update UTC timestamp."""

    @field_serializer('paid_at', 'created_at', 'updated_at')
    @classmethod
    def serialize_datetime(cls, v: datetime | None) -> int | None:
        """Converts UTC datetime fields to Unix Epoch milliseconds for Flutter.

        Args:
            v: Datetime instance or None.

        Returns:
            Integer epoch milliseconds or None.
        """
        if v is None:
            return None
        return int(v.timestamp() * 1000)