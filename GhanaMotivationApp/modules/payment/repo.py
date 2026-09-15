from typing import Sequence
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.core import PaymentStatusEnum
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


    async def atomic_mark_success(
        self, payment_id: int, new_status: str
    ) -> bool:
        """Atomically transitions a payment from PENDING to a new status.

        Uses a conditional UPDATE with WHERE status='pending' to prevent
        double-activation from concurrent requests (race condition guard).

        Args:
            payment_id: The payment's primary key.
            new_status: The target status string (e.g., 'success').

        Returns:
            True if the row was updated (status was 'pending').
            False if no row was updated (already transitioned).
        """
        from datetime import datetime, timezone

        stmt = (
            update(self.model)
            .where(
                self.model.id == payment_id,
                self.model.status == PaymentStatusEnum.PENDING.value,
            )
            .values(
                status=new_status,
                paid_at=datetime.now(timezone.utc) if new_status == PaymentStatusEnum.SUCCESS.value else None,
            )
        )
        result = await self.session.execute(stmt)
        return result.rowcount > 0