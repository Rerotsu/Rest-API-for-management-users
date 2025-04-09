# LiteStar CRUD API для Пользователей (User) с PostgreSQL

Это пример REST API, созданного на Python с использованием фреймворка LiteStar (v2.15.2) для выполнения CRUD-операций (Create, Read, Update, Delete) над сущностью "Пользователь" в базе данных PostgreSQL. Проект использует Advanced SQLAlchemy для взаимодействия с БД и Docker для контейнеризации.

## Стек Технологий

* **Backend:** [LiteStar](https://litestar.dev/) (v2.x)
* **База данных:** PostgreSQL
* **ORM/Инструменты БД:** [Advanced SQLAlchemy](https://github.com/litestar-org/advanced-alchemy), [Alembic](https://alembic.sqlalchemy.org/) (для миграций), `psycopg` (драйвер БД для Alembic), `asyncpg` (асинхронный драйвер БД для LiteStar)
* **Управление зависимостями:** [Poetry](https://python-poetry.org/) (v2.1.2)
* **Контейнеризация:** Docker, Docker Compose
* **Сервер:** Uvicorn
* **Хэширование паролей:** Passlib (bcrypt)
* **DTO:** msgspec

## Предварительные требования

* [Docker](https://docs.docker.com/engine/install/)
* [Docker Compose](https://docs.docker.com/compose/install/) (обычно устанавливается вместе с Docker Desktop)
* [Poetry](https://python-poetry.org/docs/#installation) (версия 2.1.2 или выше)

## Установка и Запуск (с Docker)

1.  **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/Rerotsu/Rest-API-for-management-users
    cd <ПАПКА ПРОЕКТА>
    ```

2.  **Создайте и настройте файл `.env`:**
    * (в проекте есть готовый `.env`)
    * Заполните его необходимыми значениями. Пример:
        ```env
        # Настройки приложения
        APP_HOST=0.0.0.0
        APP_PORT=8000
        APP_RELOAD=false # false для Docker в продакшене/стейджинге
        APP_DEBUG=false  # false для Docker в продакшене/стейджинге

        # Настройки базы данных PostgreSQL
        DB_USER=myuser
        DB_PASSWORD=mypassword
        DB_HOST=db # Имя сервиса в docker-compose.yml
        DB_PORT=5432
        DB_NAME=mydb
        DB_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

        # Опционально: Секретный ключ
        # SECRET_KEY=your_super_secret_key
        ```
    * **Важно:** Учетные данные (`DB_USER`, `DB_PASSWORD`, `DB_NAME`) в `.env` должны совпадать с переменными `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` для сервиса `db` в `docker-compose.yml`.

3.  **Соберите и запустите контейнеры:**
    ```bash
    docker-compose up --build -d
    ```
    * `--build`: Принудительная пересборка образов (если были изменения в Dockerfile или зависимостях).
    * `-d`: Запуск в фоновом режиме.

4.  **Выполните миграции базы данных:**
    * При первом запуске или после изменений в моделях (`src/models/`) нужно применить миграции. Выполните команду внутри контейнера `app`:
        ```bash
        docker-compose exec app alembic upgrade head
        ```
    * *Примечание:* При самом первом запуске таблицы могут быть созданы автоматически функцией `create_database_tables` в `on_startup`, но использование Alembic (`upgrade head`) является более правильным подходом для управления схемой БД.

## Использование API

* **Базовый URL:** Приложение будет доступно по адресу `http://localhost:8000` (если вы не меняли порт хоста `8000` в `docker-compose.yml`).
* **Документация OpenAPI (Swagger UI):** `http://localhost:8000/schema/swagger`
* **Health Check:** `http://localhost:8000/health`
* **БД** Добавляете в pgAdmin4 согласно выставленными данными
(в готовом `.env` они проставлены -
`DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db 
DB_PORT=5432
DB_NAME=RAFU`)

### Эндпоинты Пользователей (`/users`)

* **`POST /users`**: Создать нового пользователя.
    * Тело запроса (JSON):
        ```json
        {
          "name": "Имя",
          "surname": "Фамилия",
          "password": "password123"
        }
        ```
* **`GET /users`**: Получить список пользователей (поддерживает параметры `limit` и `offset` для пагинации).
    * Пример: `GET /users?limit=10&offset=0`
* **`GET /users/{user_id}`**: Получить пользователя по ID.
    * Пример: `GET /users/1`
* **`PUT /users/{user_id}`**: Обновить данные пользователя по ID.
    * Тело запроса (JSON, можно передавать только изменяемые поля):
        ```json
        {
          "name": "НовоеИмя",
          "surname": "НоваяФамилия"
        }
        ```
* **`DELETE /users/{user_id}`**: Удалить пользователя по ID.
    * Пример: `DELETE /users/1`

## Миграции Базы Данных (Alembic)

Alembic используется для управления изменениями схемы базы данных.

* **Создание новой миграции (после изменения моделей в `src/models/`):**
    * Выполните команду **на хост-машине** (где установлен Poetry и зависимости, включая Alembic и `psycopg`) или внутри контейнера `app`:
        ```bash
        # На хосте (убедитесь, что БД доступна по localhost:<порт_хоста_БД> или как настроено в alembic.ini)
        poetry run alembic revision --autogenerate -m "Краткое описание изменений"

        # Или внутри контейнера app
        docker-compose exec app alembic revision --autogenerate -m "Краткое описание изменений"
        ```
    * Проверьте сгенерированный файл миграции в папке `migrations/versions/`.

* **Применение миграций:**
    * Чтобы применить все ожидающие миграции к базе данных:
        ```bash
        docker-compose exec app alembic upgrade head
        ```

* **Откат последней миграции:**
    ```bash
    docker-compose exec app alembic downgrade -1
    ```



## Структура Проекта


litestar-crud-app/
├── .env                   # Переменные окружения (локальные, не коммитить!)
├── .gitignore             # Файл для Git ignore
├── Dockerfile             # Dockerfile для приложения
├── docker-compose.yml     # Конфигурация Docker Compose
├── poetry.lock            # Файл блокировки Poetry
├── pyproject.toml         # Зависимости и конфигурация проекта
├── alembic.ini            # Конфигурация Alembic
├── migrations/            # Директория с миграциями Alembic
│   ├── versions/          # Файлы миграций
│   ├── env.py             # Скрипт окружения Alembic
│   └── script.py.mako     # Шаблон для генерации миграций
└── src/                   # Исходный код приложения
├── init.py
├── app.py             # Фабрика приложения LiteStar
├── controllers/       # Контроллеры API (обработчики запросов)
│   └── user.py
├── dtos/              # DTO (Data Transfer Objects)
│   └── user.py
├── lib/               # Общие утилиты/конфигурации
│   ├── constants.py
│   ├── db.py          # Настройка БД и плагина SQLAlchemy
│   └── exceptions.py
├── models/            # Модели SQLAlchemy (описание таблиц БД)
│   └── user.py
└── repositories/      # Репозитории (логика доступа к данным)
