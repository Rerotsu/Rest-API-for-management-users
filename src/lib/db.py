import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig, SQLAlchemyPlugin
from advanced_alchemy.base import AuditColumns, BigIntPrimaryKey, CommonTableAttributes


load_dotenv()
DB_URL = os.getenv("DB_URL", "postgresql+asyncpg://user:pass@host:port/db")


engine = create_async_engine(DB_URL, echo=False) # echo=True для отладки SQL запросов


session_maker = async_sessionmaker(engine, expire_on_commit=False)


sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=DB_URL,
    session_maker=session_maker,
    # dependency_key="db_session", # Ключ для инъекции зависимости (по умолчанию 'db_session')
)


sqlalchemy_plugin = SQLAlchemyPlugin(config=sqlalchemy_config)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор для получения асинхронной сессии SQLAlchemy."""
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_database_tables() -> None:
    """Создает таблицы в базе данных (если их нет)."""
    from src.models.user import UserBase
    async with engine.begin() as conn:
        await conn.run_sync(UserBase.metadata.create_all)
    print("Database tables checked/created.")

async def dispose_engine() -> None:
    """Закрывает соединение с БД."""
    await engine.dispose()
    print("Database connection pool disposed.")
