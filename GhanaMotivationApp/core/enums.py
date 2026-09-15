"""Core domain enumeration abstractions.

Provides centralized enumeration classes for system-wide static domains,
such as supported currencies and payment transaction states.
"""

from enum import StrEnum

class EnvironmentEnum(StrEnum):
    """Application runtime environment modes."""

    DEVELOPMENT = "development"
    """Local development mode with relaxed validation."""

    PRODUCTION = "production"
    """Production mode with strict secret validation."""

class TokenTypeEnum(StrEnum):
    """JWT token type discriminator for dual-token authentication."""

    ACCESS = "access"
    """Short-lived token for API request authorization."""

    REFRESH = "refresh"
    """Long-lived token for session renewal, stored server-side.""" 


class CurrencyEnum(StrEnum):
    """Supported transaction currencies across the system."""

    GHANA = 'GHS'
    """Ghanaian Cedi currency identifier."""


class SubscriptionStatusEnum(StrEnum):
    """Subscription lifecycle state progression values."""

    ACTIVE = "active"
    """Subscription is currently valid and granting premium access."""

    EXPIRED = "expired"
    """Subscription period has ended without renewal."""

    CANCELLED = "cancelled"
    """Subscription was explicitly cancelled by user or system."""

class PaymentStatusEnum(StrEnum):
    """Paystack payment transaction state progression status values."""

    PENDING = 'pending'
    """Transaction initialized and awaiting customer payment."""

    SUCCESS = 'success'
    """Transaction successfully processed and funds settled."""

    FAILED = 'failed'
    """Transaction failed due to insufficient funds or rejection."""

    ABANDONED = 'abandoned'
    """Customer closed checkout window without completing payment."""

    CANCELLED = 'cancelled'
    """Transaction manually cancelled before completion."""
