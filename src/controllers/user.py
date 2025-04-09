from typing import List, Optional
import msgspec

from litestar import Controller, get, post, put, delete
from litestar.di import Provide
from litestar.params import Parameter
from litestar.exceptions import NotFoundException, ClientException
from litestar.status_codes import HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_409_CONFLICT


from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from src.repositories.user import UserRepository, provide_user_repo
from src.dtos.user import (UserCreateDTO,
                           UserReadDTO,
                           UserUpdateDTO,
                           UserListDTO)
from src.models.user import User
from src.lib.constants import USER_TAG
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


class UserController(Controller):
    path = "/users"
    tags = [USER_TAG]
    dependencies = {"user_repo": Provide(provide_user_repo, sync_to_thread=False)}

    @post(status_code=HTTP_201_CREATED, summary="Создать пользователя",
          description="Создает новую запись пользователя.")
    async def create_user(
        self,
        data: UserCreateDTO,
        user_repo: UserRepository
    ) -> UserReadDTO:
        """Создает нового пользователя."""
        hashed_pwd = hash_password(data.password)
        user_data = msgspec.to_builtins(data)
        user_data['password'] = hashed_pwd

        try:
            user_instance = User(**user_data)
            created_user = await user_repo.add(user_instance)
            await user_repo.session.commit()
            await user_repo.session.refresh(created_user)
        except IntegrityError as e:
            await user_repo.session.rollback()
            raise ClientException(status_code=HTTP_409_CONFLICT, detail=f"Database integrity error: {e}") from e
        except Exception:
            await user_repo.session.rollback()
            raise

        user_dict = created_user.to_dict()
        user_dict.pop('password', None)
        return UserReadDTO(**user_dict)

    @get(summary="Получить список пользователей",
         description="Возвращает список всех пользователей.")
    async def list_users(
        self,
        user_repo: UserRepository,
        limit: int = Parameter(default=100, ge=1, le=500, query="limit", required=False),
        offset: int = Parameter(default=0, ge=0, query="offset", required=False)
    ) -> List[UserListDTO]:
        """Возвращает список пользователей с пагинацией."""
        stmt = select(User).offset(offset).limit(limit)
        result = await user_repo.session.execute(stmt)
        users = result.scalars().all()

        results = []
        for user in users:
            user_dict = user.to_dict()
            list_dto_data = {
                "id": user_dict.get("id"),
                "name": user_dict.get("name"),
                "surname": user_dict.get("surname"),
            }
            results.append(UserListDTO(**list_dto_data))
        return results

    @get("/{user_id:int}", summary="Получить пользователя по ID",
         description="Возвращает данные одного пользователя по его ID.")
    async def get_user(
        self,
        user_id: int,
        user_repo: UserRepository
    ) -> UserReadDTO:
        """Получает пользователя по ID."""
        user = await user_repo.get_one_or_none(id=user_id)
        if not user:
            raise NotFoundException(detail=f"User with id {user_id} not found")

        user_dict = user.to_dict()
        user_dict.pop('password', None)
        return UserReadDTO(**user_dict)

    @put("/{user_id:int}", summary="Обновить пользователя",
         description="Обновляет данные существующего пользователя.")
    async def update_user(
        self,
        user_id: int,
        data: UserUpdateDTO,
        user_repo: UserRepository
    ) -> UserReadDTO:
        """Обновляет пользователя по ID."""
        user_to_update = await user_repo.get_one_or_none(id=user_id)
        if not user_to_update:
            raise NotFoundException(detail=f"User with id {user_id} not found")

        update_data = msgspec.to_builtins(data)

        if 'password' in update_data and update_data['password']:
            update_data['password'] = hash_password(update_data['password'])
        elif 'password' in update_data:
            del update_data['password']

        for key, value in update_data.items():
            if value is not None:
                setattr(user_to_update, key, value)

        try:
            user_repo.session.add(user_to_update)
            await user_repo.session.commit()
            await user_repo.session.refresh(user_to_update)
        except Exception:
            await user_repo.session.rollback()
            raise

        user_dict = user_to_update.to_dict()
        user_dict.pop('password', None)
        return UserReadDTO(**user_dict)

    @delete("/{user_id:int}", status_code=HTTP_204_NO_CONTENT,
            summary="Удалить пользователя",
            description="Удаляет пользователя по его ID.")
    async def delete_user(
        self,
        user_id: int,
        user_repo: UserRepository
    ) -> None:
        """Удаляет пользователя по ID."""
        user_to_delete = await user_repo.get_one_or_none(id=user_id)
        if not user_to_delete:
            return

        try:
            await user_repo.delete(user_id)
            await user_repo.session.commit()
        except Exception:
            await user_repo.session.rollback()
            raise

        return None
