from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from GhanaMotivationApp.database import BaseRepository
from .model import User

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(class_=User, session=session)


    async def get_by_email(self, email: str) -> User | None:
        return await self.get_one_by_attribute(email=email)


    async def check_if_exist_by_email(self, email: str) -> bool:
        return await self.get_one_by_attribute(email=email) is not None


    async def get_by_email_or_fingerprint(
        self,
        email: str,
        device_fingerprint: str
    ) -> User | None:

        stmt = (
            select(self.model)
            .where(
                or_(
                    self.model.email == email.lower(),
                    self.model.device_fingerprint == device_fingerprint
                )
            )
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_users(self, skip: int = 0, limit: int = 20) -> list[User]:
        stmt = (
            select(self.model)
            .where(self.model.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())