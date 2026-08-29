"""Authentication domain router.

Provides HTTP endpoints for user registration, login, and token refresh.
These endpoints are publicly accessible (except refresh, which requires
a valid token) and handle the conversion between Pydantic schemas and
domain services.
"""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.settings import settings
from GhanaMotivationApp.database import get_session
from GhanaMotivationApp.modules.user import User, UserResponse
from .dependencies import get_current_user
from .schemas import RegisterRequest, LoginRequest, TokenResponse
from . import service

router = APIRouter(prefix=f"{settings.API_PREFIX}/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Creates a new user account with a hashed password.",
)
async def register(
    request: RegisterRequest,
    session: AsyncSession = Depends(get_session),
) -> UserResponse:
    """Registers a new user and returns the user profile."""
    user = await service.register_user(schema=request, session=session)
    
    return UserResponse.model_validate(user)



# هي نقطة النهاية مشان نقدر نستخدم `OAuth` بال واجهة التفاعلية تبع اطار العمل 
@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    # 1. تحويل البيانات القادمة من Swagger إلى Mymodel/Schema الخاص بك
    # Swagger يرسل البريد الإلكتروني في حقل اسمه username إجبارياً
    login_request = LoginRequest(
        email=form_data.username, 
        password=form_data.password
    )
    
    # 2. استدعاء دالة السيرفيس الخاصة بك بدون أي تغيير
    token_response = await service.login_user(schema=login_request, session=session)
    
    # 3. إرجاع النتيجة بالشكل الذي يفهمه Swagger (يجب إضافة token_type)
    return {
        "access_token": token_response.access_token,
        "token_type": "bearer"
    }

# هي هية نقطة النهاية النظامية مشان وقت التشغيل النظامي
# @router.post(
#     "/login",
#     response_model=TokenResponse,
#     status_code=status.HTTP_200_OK,
#     summary="Login and get token",
#     description="Authenticates user credentials and returns a JWT access token.",
# )
# async def login(
#     request: LoginRequest,
#     session: AsyncSession = Depends(get_session),
# ) -> TokenResponse:
#     """Authenticates a user and issues a JWT token."""
#     return await service.login_user(schema=request, session=session)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description=(
        "Issues a new JWT access token with a fresh expiration time. "
        "Requires a currently valid Bearer token in the Authorization header."
    ),
)
async def refresh(
    current_user: User = Depends(get_current_user),
) -> TokenResponse:
    """Refreshes the current authenticated session."""
    return await service.refresh_token(current_user=current_user)
