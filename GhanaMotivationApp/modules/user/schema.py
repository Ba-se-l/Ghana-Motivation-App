"""User domain Pydantic schemas.

Provides request and response validation schemas for user management,
password changes, and profile status serialization.
"""

from datetime import datetime
from pydantic import BaseModel as Base, ConfigDict, Field, field_serializer


class _C(Base):
    """Base schema configuration allowing ORM model attribute access."""

    model_config = ConfigDict(from_attributes=True)


class ChangePasswordRequest(Base):
    """Request schema for changing an authenticated user's password."""

    old_password: str = Field(..., min_length=8)
    """The current plain-text password for verification."""

    new_password: str = Field(..., min_length=8, max_length=100)
    """The new plain-text password to set."""


class UserResponse(_C):
    """Serialized user entity returned in API responses.

    Converts datetimes into Epoch milliseconds for Flutter client compatibility.
    """

    id: int
    """Unique integer identifier for the user."""

    email: str
    """User's unique email address."""

    name: str | None
    """User's full display name."""

    device_fingerprint: str | None
    """Unique hardware/device fingerprint string."""

    trial_start: datetime
    """UTC timestamp when the 3-day free trial started."""

    trial_end: datetime
    """UTC timestamp when the 3-day free trial expires."""

    is_premium: bool
    """Flag indicating active paid subscription status."""

    premium_expires: datetime | None
    """UTC timestamp when premium access expires, or None if not premium."""

    is_active: bool
    """Flag indicating whether the user account is active."""

    created_at: datetime
    """Account creation UTC timestamp."""

    updated_at: datetime
    """Account last update UTC timestamp."""

    @field_serializer(
        'trial_start',
        'trial_end',
        'premium_expires',
        'created_at',
        'updated_at',
    )
    @classmethod
    def serialize_datetime(cls, v: datetime | None) -> int | None:
        """Serializes UTC datetime instances to Unix Epoch milliseconds for Flutter.

        Args:
            v: Datetime instance or None.

        Returns:
            Integer epoch milliseconds or None.
        """
        if v is None:
            return None
        return int(v.timestamp() * 1000)


class UserStatusResponse(Base):
    """Full user status payload returned by `GET /users/status`."""

    user: UserResponse
    """Serialized user profile object."""

    trial_remaining_seconds: int
    """Remaining trial duration in seconds (0 if expired)."""

    is_premium: bool
    """Flag indicating whether the user has active premium status."""

    is_trial_active: bool
    """Flag indicating whether the user is within an active free trial period."""

    premium_expires: datetime | None
    """Expiration timestamp of current premium subscription."""


class UserRegistrationResponse(UserStatusResponse):
    """Full response payload for user registration endpoint."""