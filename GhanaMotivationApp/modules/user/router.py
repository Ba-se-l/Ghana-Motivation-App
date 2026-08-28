"""User domain router.

Provides HTTP endpoints for managing user profiles. All endpoints
require a valid JWT token via the ``get_current_user`` dependency.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, status, Query

from GhanaMotivationApp.settings import settings
from GhanaMotivationApp.database import get_session
from GhanaMotivationApp.modules.auth.dependencies import get_current_user
from .model import User
from .schema import UserResponse, ChangePasswordRequest, UserStatusResponse
from . import service

router = APIRouter(prefix=f"{settings.API_PREFIX}/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Returns the profile of the currently authenticated user."""
    return UserResponse.model_validate(current_user)


@router.get(
    '/status',
    response_model=UserStatusResponse,
    status_code=status.HTTP_200_OK,
    summary='Get user subscription status.'
)
async def get_status(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
) -> UserStatusResponse:
    """Returns trial/premium status with computed dynamic fields."""

    return await service.get_user_status(
        user_id=current_user.id,
        session=session
    )


@router.patch(
    "/me/password",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Change user password",
)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """Changes the user's password. Requires the old password to verify."""
    user = await service.change_password(
        user_id=current_user.id,
        schema=request,
        session=session,
    )
    return UserResponse.model_validate(user)


