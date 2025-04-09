from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, String, func, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import BIGINT

from advanced_alchemy.base import BigIntBase

if TYPE_CHECKING:
    from typing import Optional 


class UserBase(BigIntBase):
    """Базовая модель SQLAlchemy для таблицы user с BIGINT ID."""
    id: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    __abstract__ = True


class User(UserBase):
    """Модель пользователя."""
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100))
    surname: Mapped[str] = mapped_column(String(100))
    password: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, surname={self.surname!r})"
