from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.core import SubscriptionStatusEnum
from GhanaMotivationApp.database import BaseRepository
from .model import Subscription


class SubscriptionRepository(BaseRepository[Subscription]):
    """Repository for Subscription CRUD and lifecycle operations.

    Attributes:
        model: The Subscription ORM class.
        session: The active async database session.
    """

    def __init__(self, session: AsyncSession):
        """Initializes with the Subscription model.

        Args:
            session: The active async database session.
        """
        super().__init__(Subscription, session)

    async def get_active_subscription(self, user_id: int) -> Subscription | None:
        """Finds the currently active subscription for a user.

        Args:
            user_id: The user's primary key.

        Returns:
            The active Subscription instance or None.
        """
        return await self.get_one_by_attribute(
            user_id=user_id,
            status=SubscriptionStatusEnum.ACTIVE.value,
        )

    async def deactivate_all_for_user(self, user_id: int) -> None:
        """Sets all active subscriptions for a user to 'expired'.

        Called before creating a new subscription to ensure only one
        active row exists per user at any time.

        Args:
            user_id: The user's primary key.
        """
        stmt = (
            update(Subscription)
            .where(
                Subscription.user_id == user_id,
                Subscription.status == SubscriptionStatusEnum.ACTIVE.value,
            )
            .values(status=SubscriptionStatusEnum.EXPIRED.value)
        )
        await self.session.execute(stmt)

    async def expire_subscription(self, subscription_id: int) -> None:
        """Explicitly marks a single subscription as expired.

        Args:
            subscription_id: The subscription's primary key.
        """
        stmt = (
            update(Subscription)
            .where(Subscription.id == subscription_id)
            .values(status=SubscriptionStatusEnum.EXPIRED.value)
        )
        await self.session.execute(stmt)
