from typing import List, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from src.models.user import User
from src.dtos.user import UserCreateDTO, UserUpdateDTO


class UserRepository(SQLAlchemyAsyncRepository[User]):
    """Репозиторий для операций с пользователями."""
    model_type = User


def provide_user_repo(db_session: AsyncSession) -> UserRepository:
    """Предоставляет экземпляр UserRepository с активной сессией."""
    return UserRepository(session=db_session)
