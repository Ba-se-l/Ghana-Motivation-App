"""Core domain enumeration abstractions.

Provides centralized enumeration classes for system-wide static domains,
such as supported currencies and payment transaction states.
"""

from enum import StrEnum


class CurrencyEnum(StrEnum):
    """Supported transaction currencies across the system."""

    GHANA = 'GHS'
    """Ghanaian Cedi currency identifier."""


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