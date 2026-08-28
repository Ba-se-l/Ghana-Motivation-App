from typing import Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.database import BaseRepository
from .model import Payment


class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session: AsyncSession):
        super().__init__(class_=Payment, session=session)


    async def get_by_reference(self, reference: str) -> Payment | None:
        return await self.get_one_by_attribute(reference=reference)


    async def get_payments_by_user(self,
        user_id: int, offset: int = 0, limit: int = 20
    ) -> Sequence[Payment]:

        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()


    