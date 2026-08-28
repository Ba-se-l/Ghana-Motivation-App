from pydantic import BaseModel as Base, ConfigDict,  Field
from datetime import datetime

from GhanaMotivationApp.core import CurrencyEnum

class _C(Base):
    model_config = ConfigDict(from_attributes=True)

class InitSubscriptionRequest(Base):
    """POST /initialize_subscription request body."""
    user_id: int = Field(...)
    email: str = Field(..., min_length=5, max_length=100, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    amount: int = Field(..., gt=0, description="Amount in pesewas (minor units)")


class PaymentInitResponse(Base):
    """POST /initialize_subscription response."""
    authorization_url: str
    reference: str


class VerifyTransactionResponse(Base):
    """GET /verify_transaction response — passthrough from Paystack."""
    status: str
    message: str
    data: dict


class PaymentResponse(_C):
    id: int
    reference: str
    amount: int
    currency: CurrencyEnum
    status: str
    paid_at: datetime | None 
    user_id: int
    created_at: datetime
    updated_at: datetime