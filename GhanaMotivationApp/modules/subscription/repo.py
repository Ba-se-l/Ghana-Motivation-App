from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.database import BaseRepository
from .model import Subscription


class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session: AsyncSession):
        super().__init__(Subscription, session)

    async def get_active_subscription(self, user_id: int) -> Subscription | None:
        """Finds the currently active subscription for a user."""
        return await self.get_one_by_attribute(user_id=user_id, active=True)