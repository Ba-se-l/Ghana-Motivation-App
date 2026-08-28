"""Authentication module public API.

Exposes request/response schemas and the FastAPI router.
"""

from .schemas import RegisterRequest, LoginRequest, TokenResponse
from .router import router

__all__ = (
    # from schemas.py
    'RegisterRequest',
    'LoginRequest',
    'TokenResponse',

    # from router.py
    'router',
)
