from pydantic import BaseModel as Base
from pydantic import Field
from pydantic import ConfigDict

from datetime import datetime


class _C(Base):
    model_config = ConfigDict(from_attributes=True)


class CreateUserRequest(Base):
    """POST /users/register request body."""
    name: str | None = Field(
        min_length=5,
        max_length=20,
        default=None
    )

    email: str = Field(
        ...,
        min_length=10,
        max_length=200,
        pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$'
    )

    password: str = Field(
        ...,
        min_length=8,
        max_length=50
    )

    device_fingerprint: str = Field(
        ...,
        min_length=1,
        max_length=200,
        examples=['DEVICE_ID']
    )



class ChangePasswordRequest(Base):
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(_C):
    """Serialized user entity returned in API responses."""
    id: int
    email: str
    name: str | None
    device_fingerprint: str | None
    trial_start: datetime
    trial_end: datetime
    is_premium: bool
    premium_expires: datetime | None
    created_at: datetime
    updated_at: datetime

class UserStatusResponse(Base):
    """GET /users/status — full status payload."""
    user: UserResponse
    trial_remaining_seconds: int
    is_premium: bool
    is_trial_active: bool
    premium_expires: datetime | None


class UserRegistrationResponse(UserStatusResponse):
    """POST /users/register — full registration payload."""