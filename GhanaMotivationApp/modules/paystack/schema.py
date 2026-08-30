from pydantic import BaseModel

from GhanaMotivationApp.core import CurrencyEnum

class PaystackInitRequest(BaseModel):
    """Data sent TO Paystack to initialize a transaction."""
    email: str
    amount: int
    """Amount in pesewas (minor units). 1000 = 10.00 GHS."""
    currency: CurrencyEnum = CurrencyEnum.GHANA
    callback_url: str | None = None


class PaystackInitResponseData(BaseModel):
    """The 'data' object inside Paystack's initialize response."""
    authorization_url: str
    access_code: str
    reference: str


class PaystackInitResponse(BaseModel):
    """Full response from POST https://api.paystack.co/transaction/initialize."""
    status: bool
    message: str
    data: PaystackInitResponseData


class PaystackVerifyResponseData(BaseModel):
    """The 'data' object inside Paystack's verify response."""
    status: str
    """'success', 'failed', 'abandoned'"""
    reference: str
    amount: int
    currency: CurrencyEnum
    paid_at: str | None = None
    customer: dict


class PaystackVerifyResponse(BaseModel):
    """Full response from GET https://api.paystack.co/transaction/verify/:reference."""
    status: bool
    message: str
    data: PaystackVerifyResponseData