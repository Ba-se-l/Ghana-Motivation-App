"""Authentication domain service layer.

Handles user registration, login (JWT issuance), and token refresh.
Each function orchestrates calls to ``UserRepository`` and ``core.security``
without implementing low-level data access itself.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.core import (
    hash_password,
    verify_password,
    create_access_token,
    InvalidCredentialsException,
)
from GhanaMotivationApp.settings import settings
from GhanaMotivationApp.modules.user import User, UserRepository, UserAlreadyExistsException, UserInactiveException
from .schemas import RegisterRequest, LoginRequest, TokenResponse


async def register_user(schema: RegisterRequest, session: AsyncSession) -> User:
    """Registers a new user account.

    Orchestration steps:
        1. Check if the email is already taken.
        2. Hash the plain-text password.
        3. Create the ``User`` ORM instance.
        4. Persist via ``UserRepository.create``.

    Args:
        schema: The validated registration request.
        session: The active database session.

    Returns:
        The newly created ``User`` ORM instance.

    Raises:
        UserAlreadyExistsException: If the email is already registered.
    """
    user_repo = UserRepository(session=session)

    # Step 1: Check email uniqueness
    is_user_exist = await user_repo.check_if_exist_by_email(schema.email)
    if is_user_exist:
        raise UserAlreadyExistsException(field='email', value=schema.email)

    # Step 2: Hash the password
    hashed_password = hash_password(plain_password=schema.password)

    now = datetime.now(timezone.utc)
    trial_end = now + timedelta(days=settings.TRIAL_DAYS) 

    # Step 3: Build the ORM model
    orm_model = User(
        name=schema.name,
        email=schema.email,
        hashed_password=hashed_password,
        trial_start=now,
        trial_end=trial_end,
        is_premium=False,
        device_fingerprint=schema.device_fingerprint
    )

    # Step 4: Persist and return
    user = await user_repo.create(orm_model=orm_model)

    await session.flush()
    
    return user


async def login_user(schema: LoginRequest, session: AsyncSession) -> TokenResponse:
    """Authenticates a user and issues a JWT access token.

    Orchestration steps:
        1. Fetch the user by email.
        2. Verify the password hash.
        3. Check that the user account is active.
        4. Generate and return the JWT access token.

    Args:
        schema: The validated login request containing email and password.
        session: The active database session.

    Returns:
        A ``TokenResponse`` containing the JWT ``access_token``.

    Raises:
        InvalidCredentialsException: If the email or password is wrong.
        UserInactiveException: If the user account is deactivated.
    """
    user_repo = UserRepository(session=session)

    # Step 1: Fetch user by email
    user = await user_repo.get_by_email(schema.email)
    if user is None:
        raise InvalidCredentialsException()

    # Step 2: Verify the password
    is_hashed_match = verify_password(
        plain_password=schema.password,
        hashed_password=user.hashed_password,
    )
    if not is_hashed_match:
        raise InvalidCredentialsException()

    # Step 3: Verify the account is active
    if not user.is_active:
        raise UserInactiveException(identifier=str(user.id))

    # Step 4: Issue JWT access token
    access_token = create_access_token(user_id=user.id)

    return TokenResponse(access_token=access_token)


async def refresh_token(current_user: User) -> TokenResponse:
    """Issues a new JWT access token for an already-authenticated user.

    This endpoint allows clients to extend their session without
    re-entering credentials. The caller must provide a valid (non-expired)
    JWT token via the ``get_current_user`` dependency.

    Args:
        current_user: The authenticated ``User`` ORM instance
            (injected by ``get_current_user``).

    Returns:
        A ``TokenResponse`` containing a fresh JWT ``access_token``
        with a new expiration timestamp.
    """
    access_token = create_access_token(user_id=current_user.id)

    return TokenResponse(access_token=access_token)