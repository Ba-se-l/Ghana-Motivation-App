from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.database import BaseRepository
from .model import Quote


class QuoteRepository(BaseRepository[Quote]):
    def __init__(self, session: AsyncSession):
        super().__init__(Quote, session)

    async def get_by_day_number(self, day_number: int) -> Quote | None:
        """Retrieves the quote for a specific day (1-365)."""
        return await self.get_one_by_attribute(day_number=day_number)

    async def get_random_quote(self) -> Quote | None:
        """Retrieves a random active quote."""
        stmt = select(self.model).where(self.model.is_active == True).order_by(func.random()).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


    