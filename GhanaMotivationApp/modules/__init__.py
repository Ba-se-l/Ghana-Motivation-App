from fastapi import APIRouter

from .auth import router as auth_router
from .user import router as user_router
from .payment import router as payment_router
from .quote.router import router as quote_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(user_router)
api_router.include_router(payment_router)
api_router.include_router(quote_router)

__all__ = ('api_router',)