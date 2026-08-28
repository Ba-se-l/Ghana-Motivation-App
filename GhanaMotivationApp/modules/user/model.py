from typing import TYPE_CHECKING
from sqlalchemy import Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from GhanaMotivationApp.database import Base
from GhanaMotivationApp.database import CreatedAtUpdatedAtMixin


if TYPE_CHECKING:
    from GhanaMotivationApp.modules.payment import Payment
    from GhanaMotivationApp.modules.subscription import Subscription


class User(Base, CreatedAtUpdatedAtMixin):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        default=None
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    device_fingerprint: Mapped[str | None] = mapped_column(
        String(255), 
        index=True,
        nullable=True,
        default=None
    )

    trial_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    trial_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    is_premium: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    premium_expires: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True
    )

    payments: Mapped[list['Payment']] = relationship(back_populates='user')
    subscriptions: Mapped[list['Subscription']] = relationship(back_populates='user')

    def __repr__(self):
        return (
            f"User(id={self.id}, name={self.name}, email={self.email}, "
            f"trail_start={self.trail_start}, is_premium={self.is_premium}, is_active={self.is_active}, "
            f"premium_expires={self.premium_expires})"
        )