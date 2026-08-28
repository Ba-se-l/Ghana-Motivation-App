from typing import TYPE_CHECKING
from sqlalchemy import Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from GhanaMotivationApp.database.base import Base
from GhanaMotivationApp.database.mixin import CreatedAtUpdatedAtMixin


if TYPE_CHECKING:
    from GhanaMotivationApp.modules.user import User

class Subscription(CreatedAtUpdatedAtMixin, Base):
    __tablename__ = 'subscriptions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('users.id')
    )

    start_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    next_billing: Mapped[datetime] = mapped_column(
        DateTime(timezone=True)
    )

    active: Mapped[bool] = mapped_column(Boolean, default=True)

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="subscriptions")