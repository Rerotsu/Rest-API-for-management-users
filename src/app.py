import os
from typing import Any, Dict

import uvicorn
from dotenv import load_dotenv
from litestar import Litestar, Request, get
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig
from litestar.logging.config import LoggingConfig

from src.controllers.user import UserController
from src.lib.db import sqlalchemy_plugin, create_database_tables, dispose_engine
from src.lib.constants import HEALTH_TAG


load_dotenv()

cors_config = CORSConfig(allow_origins=["*"])

openapi_config = OpenAPIConfig(
    title="LiteStar CRUD API",
    version="1.0.0",
    description="Простое API для управления пользователями с использованием LiteStar, SQLAlchemy и PostgreSQL.",
    contact={"name": "API Developer", "email": "lukmanov.nikia06@mail.ru", "tg": "@Rerotsu"},

)


log_config = LoggingConfig(
    loggers={
        "myapp": {
            "level": "INFO",
            "handlers": ["console"],
        }
    }
)


async def on_startup() -> None:
    """Выполняется при старте приложения."""
    print("Application startup...")

    await create_database_tables()
    print("Startup complete.")


async def on_shutdown() -> None:
    """Выполняется при остановке приложения."""
    print("Application shutdown...")

    await dispose_engine()
    print("Shutdown complete.")


@get("/health", tags=[HEALTH_TAG], summary="Проверка работоспособности", description="Возвращает статус 'OK', если приложение работает.")
async def health_check() -> Dict[str, str]:
    """Проверка состояния приложения."""
    return {"status": "OK"}


app = Litestar(
    route_handlers=[UserController, health_check],
    plugins=[sqlalchemy_plugin],
    openapi_config=openapi_config,
    cors_config=cors_config,
    logging_config=log_config,
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
    debug=bool(os.getenv("APP_DEBUG", "False").lower() == 'true'),  # Включаем режим отладки из .env
    # middleware=[...] # Можно добавить middleware

)


def run_server():
    """Запускает ASGI сервер с помощью uvicorn."""
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "8000"))
    reload = bool(os.getenv("APP_RELOAD", "False").lower() == 'true')

    uvicorn.run(
        "src.app:app",
        host=host,
        port=port,
        reload=reload,   # Включаем автоперезагрузку при изменениях кода (для разработки)
        # workers=4 # Количество рабочих процессов (для продакшена)
    )


if __name__ == "__main__":
    run_server()
