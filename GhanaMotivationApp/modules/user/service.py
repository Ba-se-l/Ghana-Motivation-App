"""User domain service layer.

Contains all business logic for user profile management operations.
Each public function acts as an orchestrator that delegates data access
to ``UserRepository`` and applies domain rules.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone


from GhanaMotivationApp.core import hash_password, verify_password, InvalidCredentialsException
from .model import User
from .schema import ChangePasswordRequest, UserStatusResponse, UserResponse
from .repo import UserRepository
from .exceptions import UserNotFoundException


async def _get_user(user_id: int, session: AsyncSession) -> User:
    """Internal helper: fetches a user by ID or raises.

    Args:
        user_id: The int of the user to fetch.
        session: The active database session.

    Returns:
        The ``User`` ORM instance.

    Raises:
        UserNotFoundException: If no user with the given ID exists.
    """
    user_repo = UserRepository(session=session)
    user = await user_repo.get_by_id(id=user_id)

    if user is None:
        raise UserNotFoundException(identifier=str(user_id))

    return user



def _calculate_trial_remaining_seconds(trial_end: datetime) -> int:
    """Calculates remaining trial seconds from server's current UTC time.

    Args:
        trial_end: The UTC timestamp when the trial expires.

    Returns:
        Remaining seconds as a non-negative integer. Returns 0 if expired.
    """
    now = datetime.now(timezone.utc)
    delta = trial_end - now
    remaining = int(delta.total_seconds())
    return max(remaining, 0)


async def _reconcile_premium_status(user: User, user_repo: UserRepository) -> User:
    """Auto-deactivates premium if premium_expires has passed.

    This is the server-authoritative reconciliation mechanism. If is_premium
    is True but premium_expires < now(), the server corrects the state.

    Args:
        user: The User ORM instance to check.
        user_repo: The repository for persisting changes.

    Returns:
        The (potentially updated) User ORM instance.
    """
    if not user.is_premium:
        return user

    if user.premium_expires is None:
        return user

    now = datetime.now(timezone.utc)
    if user.premium_expires < now:
        # Premium has expired — deactivate
        user = await user_repo.update(
            orm_model=user,
            update_data={'is_premium': False}
        )

    return user


async def soft_delete_user(user_id: int, session: AsyncSession) -> User:
    """Soft-deletes a user by deactivating their account.

    Sets ``is_active`` to ``False`` and ``status`` to ``OFFLINE``.
    The user record remains in the database for referential integrity.

    Args:
        user_id: The int of the user to deactivate.
        session: The active database session.

    Returns:
        The soft-deleted ``User`` ORM instance.

    Raises:
        UserNotFoundException: If the user does not exist.
    """
    user_repo = UserRepository(session=session)

    # Step 1: Fetch the user or raise
    user = await _get_user(user_id=user_id, session=session)

    # Step 2: Deactivate via update
    soft_deleted_user = await user_repo.update(
        orm_model=user,
        update_data={'is_active': False},
    )

    return soft_deleted_user


async def list_users(skip: int, limit: int, session: AsyncSession) -> list[User]:
    """Lists all active users with pagination.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        session: The active database session.

    Returns:
        A list of active ``User`` ORM instances.
    """
    user_repo = UserRepository(session=session)

    return await user_repo.get_active_users(skip=skip, limit=limit)


async def change_password(user_id: int, schema: ChangePasswordRequest, session: AsyncSession) -> User:
    """Changes a user's password after verifying the old one.

    The old password is verified against the stored hash. If it matches,
    the new password is hashed and stored.

    Args:
        user_id: The int of the user changing their password.
        schema: The request containing ``old_password`` and ``new_password``.
        session: The active database session.

    Returns:
        The updated ``User`` ORM instance.

    Raises:
        UserNotFoundException: If the user does not exist.
        InvalidCredentialsException: If the old password does not match.
    """
    user_repo = UserRepository(session=session)

    # Step 1: Fetch the user or raise
    user = await _get_user(user_id=user_id, session=session)

    # Step 2: Verify the old password matches
    is_password_match = verify_password(
        plain_password=schema.old_password,
        hashed_password=user.hashed_password,
    )

    if not is_password_match:
        raise InvalidCredentialsException()

    # Step 3: Hash the new password
    hashed_password = hash_password(plain_password=schema.new_password)

    # Step 4: Update via repository
    updated_user = await user_repo.update(
        orm_model=user,
        update_data={'hashed_password': hashed_password},
    )

    return updated_user



async def get_user_status(user_id: int, session: AsyncSession) -> UserStatusResponse:
    """Retrieves the full status payload for a user.

    Orchestration:
        1. Fetch the user by ID (or raise).
        2. Reconcile premium expiration.
        3. Calculate trial remaining seconds.
        4. Build and return the status response.

    Args:
        user_id: The user's primary key.
        session: The active database session.

    Returns:
        A ``UserStatusResponse`` containing user data + computed fields.

    Raises:
        UserNotFoundException: If the user does not exist.
    """

    user_repo = UserRepository(session=session)

    # Step 1: Fetch the user
    user = await _get_user(user_id=user_id, session=session)

    # Step 2: Reconcile premium status
    user = await _reconcile_premium_status(user=user, user_repo=user_repo)

    # Step 3: Calcualte dynamic fields
    trial_remaining = _calculate_trial_remaining_seconds(trial_end=user.trial_end)
    is_trial_active = trial_remaining > 0

    # Step 4: Build response
    user_response = UserResponse.model_validate(user)

    return UserStatusResponse(
        user=user_response,
        trial_remaining_seconds=trial_remaining,
        is_premium=user.is_premium,
        is_trial_active=is_trial_active,
        premium_expires=user.premium_expires
    )