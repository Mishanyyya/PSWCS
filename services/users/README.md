# Users Service

Микросервис управления пользователями на FastAPI + SQLAlchemy (async) + Alembic.

## Быстрый старт

1. Скопировать env-файл:

```bash
cp .env.example .env
```

2. Настроить значения в `.env` (минимум `DATABASE_URL` и `JWT_SECRET`).

3. Запустить проект одной командой:

```bash
make up
```

Команда `make up` делает полный цикл:

- создает venv (если нет);
- ставит зависимости;
- применяет миграции;
- создает тестовых пользователей;
- запускает сервер.

После запуска API доступен по адресу: `http://127.0.0.1:8001`.

## Что уже автоматизировано

В проекте убран критичный хардкод из:

- подключения к БД (через `DATABASE_URL`);
- JWT (через `JWT_SECRET` и `JWT_ALGORITHM`);
- SQL echo (через `SQL_ECHO`);
- роли пользователя по умолчанию (через `DEFAULT_USER_ROLE`);
- параметров сидера (через `SEED_*`).

## Переменные окружения

Все примеры есть в `.env.example`.

Основные:

- `APP_NAME` - имя приложения в OpenAPI.
- `DATABASE_URL` - async URL для приложения (пример: `postgresql+asyncpg://...`).
- `JWT_SECRET` - секрет подписи токена (обязательно поменять для production).
- `JWT_ALGORITHM` - алгоритм JWT (`HS256` по умолчанию).
- `ACCESS_TOKEN_EXPIRE_MINUTES` - TTL access-token в минутах.
- `SQL_ECHO` - включение SQL-логов (`true/false`).
- `DEFAULT_USER_ROLE` - роль пользователя при регистрации.

Для сидера:

- `SEED_ADMIN_EMAIL`
- `SEED_ADMIN_PASSWORD`
- `SEED_ADMIN_FULL_NAME`
- `SEED_USER_ROLES` (формат: `admin:0.1,user:0.9`)
- `SEED_OUTPUT_FILE`

Для запуска:

- `HOST`
- `PORT`

## Makefile команды

```bash
make help
```

Основные цели:

- `make venv` - создать виртуальное окружение.
- `make install` - установить runtime + dev зависимости.
- `make clean-venv` - удалить venv.
- `make recreate-venv` - пересоздать venv с нуля.
- `make lint` - запустить `ruff`.
- `make migrate` - применить миграции.
- `make migrate-down` - откатить последнюю миграцию.
- `make seed` - сгенерировать пользователей.
- `make bootstrap` - полный bootstrap (install + migrate + seed).
- `make run` - запустить сервис.
- `make up` - bootstrap + run одной командой.

Параметры для `make seed` можно переопределить:

```bash
make seed SEED_COUNT=50 SEED_FORCE=--force SEED_OUTPUT_FILE=tmp/users.txt
```

## Ручной запуск (без make)

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
alembic upgrade head
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```

## Структура проекта

```text
app/
  api/           # HTTP endpoints
  core/          # настройки и безопасность
  db/            # engine/session/base
  models/        # SQLAlchemy модели
  schemas/       # Pydantic схемы
  services/      # бизнес-логика
alembic/         # миграции
seed_users.py    # сидер тестовых пользователей
Makefile         # команды для разработчиков
```

## Основные API endpoints

- `POST /users/` - регистрация.
- `POST /users/login` - логин.
- `GET /users/auth/validation` - валидация bearer-токена.
- `GET /users/` - список пользователей.
- `GET /users/{id}` - получить пользователя.
- `PUT /users/{id}` - обновить пользователя.
- `DELETE /users/{id}` - удалить пользователя.

## Безопасность

- Пароли хешируются через `bcrypt`.
- JWT подпись и алгоритм берутся из env.
- Детали ошибок токена не раскрываются клиенту в ответе.

## Code Review: что стоит улучшить дальше

1. Добавить тесты (минимум smoke на auth и CRUD).
2. Добавить pre-commit (ruff + formatting + basic checks).
3. Разнести DTO для create/update (`UserUpdate` без обязательного пароля).
4. Ограничить пагинацию (`limit`) через валидацию диапазона.
5. Добавить healthcheck endpoint (`/health`) для оркестрации.
