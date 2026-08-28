from GhanaMotivationApp.core import AppException, NotFoundException


class PaymentNotFoundException(NotFoundException):
    """Raised when a payment record is not found by reference."""
    def __init__(self, reference: str):
        super().__init__(entity="Payment", identifier=reference)


class DuplicatePaymentException(AppException):
    """Raised when a payment reference already exists (idempotency guard)."""
    def __init__(self, reference: str):
        super().__init__(
            message=f"Payment with reference '{reference}' has already been processed.",
            error_code="DUPLICATE_PAYMENT",
            status_code=409,
        )


class PaymentVerificationFailedException(AppException):
    """Raised when Paystack verification returns a non-success status."""
    def __init__(self, reference: str, paystack_status: str):
        super().__init__(
            message=f"Payment '{reference}' verification failed. Paystack status: '{paystack_status}'.",
            error_code="PAYMENT_VERIFICATION_FAILED",
            status_code=400,
        )


class InvalidWebhookSignatureException(AppException):
    """Raised when Paystack webhook HMAC signature does not match."""
    def __init__(self):
        super().__init__(
            message="Invalid webhook signature.",
            error_code="INVALID_WEBHOOK_SIGNATURE",
            status_code=401,
        )