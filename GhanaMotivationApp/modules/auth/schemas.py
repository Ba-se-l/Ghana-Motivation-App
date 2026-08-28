from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """Schema for user registration request."""

    name: str = Field(..., min_length=1, max_length=100)
    """The user's full display name."""

    email: str = Field(..., min_length=5, max_length=100, pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    """The user's email address. Must be unique across the system."""

    password: str = Field(..., min_length=8, max_length=100)
    """The user's plain-text password. Will be hashed before storage."""

    device_fingerprint: str = Field(
        ...,
        min_length=1,
        max_length=200,
        examples=['DEVICE_ID']
    )


class LoginRequest(BaseModel):
    """Schema for user login request."""

    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    """The user's registered email address."""

    password: str = Field(...)
    """The user's plain-text password for verification."""


class TokenResponse(BaseModel):
    """Schema for JWT token API responses."""

    access_token: str
    """The JWT access token string."""

    token_type: str = 'bearer'
    """The token type. Always ``bearer``."""