# Users Microservice

Микросервис для управления пользователями в веб-приложении. Реализован на **FastAPI** с асинхронной работой через **SQLAlchemy** и поддержкой миграций через **Alembic**.

## Структура проекта

```
app/
├── api/              # REST API роутеры
│   └── user.py
├── core/             # Конфигурация, безопасность
│   └── security.py
├── db/               # Работа с базой данных
│   ├── models.py
│   └── session.py
├── schemas/          # Pydantic-схемы
│   └── user.py
├── services/         # Логика приложения
│   └── user_service.py
alembic/              # Миграции базы данных
requirements.txt      # Зависимости проекта
```

## Установка

Рекомендуется использовать виртуальное окружение:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

## Конфигурация

Настройки подключения к базе данных находятся в `app/db/session.py`.
Пример строки подключения PostgreSQL:

```python
DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/dbname"
```

## Миграции базы данных

Создание новой миграции:

```bash
alembic revision --autogenerate -m "описание миграции"
```

Применение миграций:

```bash
alembic upgrade head
```

## Запуск приложения

```bash
uvicorn app.main:app --reload
```

После запуска API будет доступно по адресу: `http://127.0.0.1:8000`.

## API

Основные эндпоинты для работы с пользователями:

| Метод | Путь            | Описание                          |
|-------|----------------|----------------------------------|
| POST  | /users/        | Создание пользователя             |
| POST  | /users/login   | Аутентификация пользователя      |
| GET   | /users/{id}    | Получение информации о пользователе |

Примеры запросов описаны в Pydantic схемах `UserCreate`, `UserResponse`, `UserLogin`.

### Пример запроса на создание пользователя

```bash
curl -X POST http://127.0.0.1:8000/users/ \
-H "Content-Type: application/json" \
-d '{"email": "user@example.com", "password": "securepassword"}'
```

### Пример ответа

```json
{
  "id": 1,
  "email": "user@example.com"
}
```

## Безопасность

- Пароли хранятся в хэшированном виде (используется `bcrypt`).
- JWT токены используются для аутентификации.

## Разработка

Рекомендуется использовать линтер и форматтер `ruff` для соблюдения кодстайла:

```bash
ruff check app
```
