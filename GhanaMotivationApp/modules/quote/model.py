from sqlalchemy import Integer, String, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from GhanaMotivationApp.database.base import Base
from GhanaMotivationApp.database.mixin import CreatedAtUpdatedAtMixin


class Quote(CreatedAtUpdatedAtMixin, Base):
    __tablename__ = 'quotes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    day_number: Mapped[int] = mapped_column(Integer, unique=True)

    content: Mapped[str] = mapped_column(Text)

    author: Mapped[str | None] = mapped_column(String(255), nullable=True)

    category: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)