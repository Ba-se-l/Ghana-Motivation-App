from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from GhanaMotivationApp.core import CurrencyEnum
from GhanaMotivationApp.database import Base, CreatedAtUpdatedAtMixin


if TYPE_CHECKING:
    from GhanaMotivationApp.modules.user import User

class Payment(Base, CreatedAtUpdatedAtMixin):
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    reference: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True
    )

    amount: Mapped[int] = mapped_column(Integer)

    currency: Mapped[CurrencyEnum] = mapped_column(
        Enum(CurrencyEnum),
        default=CurrencyEnum.GHANA,
    )

    status: Mapped[str] = mapped_column(String)

    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('users.id')
    )

    user: Mapped['User'] = relationship(back_populates='payments')
    