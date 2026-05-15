# UniReview API 🎓

UniReview API — это микросервисная платформа на Python с использованием FastAPI, предназначенная для сбора и модерации отзывов об университетах. Проект построен на базе трех независимых, но взаимодействующих микросервисов, что обеспечивает его масштабируемость и надежность.

## ✨ Возможности

*   **Микросервисная архитектура**: Независимые сервисы для управления пользователями (`users`), отзывами (`review`) и каталогом университетов (`university`).
*   **Асинхронность**: Все сервисы построены на асинхронном стеке FastAPI + SQLAlchemy (Async).
*   **Ролевая модель**: Поддержка ролей `user` (обычный пользователь) и `admin` (модератор).
*   **Модерация отзывов**: Отзывы проходят пре-модерацию: после создания имеют статус `pending`, и только администратор может изменить его на `approved` или `rejected`.
*   **Взаимодействие сервисов**: Сервис отзывов (`review`) напрямую обращается к сервисам `users` (для проверки токена и прав) и `university` (для проверки существования университета и обновления статистики) через HTTP клиенты.
*   **Автоматическое логирование**: Система логирует все действия модераторов.
*   **Контейнеризация**: Каждый сервис упакован в Docker, а для оркестрации используется `docker-compose`.
*   **Готовность к продакшену**: Используются современные инструменты: `bcrypt` для хеширования паролей, JWT для аутентификации, `pytest` для тестирования и `ruff` для линтинга.

## 🛠 Стек технологий

*   **Python 3.11+**
*   **FastAPI** — веб-фреймворк
*   **PostgreSQL + SQLAlchemy (Async) + Alembic** — база данных и миграции
*   **Pydantic** — валидация данных
*   **Docker & Docker Compose** — контейнеризация
*   **pytest** (с `pytest-asyncio`, `httpx`) — тестирование
*   **Ruff** — линтинг и форматирование
*   **python-jose** — JWT токены
*   **bcrypt** — хеширование паролей
*   **httpx** — асинхронные HTTP-запросы между сервисами


## 📁 Архитектура проекта

```
project/
├── docker-compose.yml            # Оркестрация всех трех сервисов
├── services/                     # Директория с микросервисами
│   ├── users/                    # Микросервис пользователей (порт 8001)
│   │   ├── app/                  # Основная логика сервиса
│   │   │   ├── api/              # Роутеры (user.py)
│   │   │   ├── core/             # Конфигурация, безопасность (security.py)
│   │   │   ├── db/               # Модели и сессия БД
│   │   │   ├── schemas/          # Pydantic-схемы (user.py)
│   │   │   └── services/         # Бизнес-логика (user_service.py)
│   │   ├── alembic/              # Миграции БД
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── review/                   # Микросервис отзывов (порт 8002)
│   │   ├── app/
│   │   │   ├── clients/          # HTTP клиенты для связи с другими сервисами
│   │   │   ├── routers/          # Роутеры (reviews.py, moderation.py)
│   │   │   ├── seeds/            # Наполнение БД тестовыми данными
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   ├── dependencies.py   # Внедрение зависимостей (get_current_user, get_db)
│   │   │   ├── models.py
│   │   │   └── schemas.py
│   │   ├── tests/                # Полный набор тестов
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── university/               # Микросервис университетов (порт 8003)
│       ├── app/
│       │   ├── api/              # Роутеры
│       │   ├── core/             # Конфигурация
│       │   ├── db/               # Модели и сессия
│       │   ├── errors/           # Обработка ошибок
│       │   ├── logger/           # Логирование
│       │   └── models/
│       ├── Dockerfile
│       └── requirements.txt
└── shared/                       # Общий код и утилиты
    └── utils/                    # (pon.py и прочее)
```

## Быстрый старт

Предварительные требования

```
Python 3.11+

Git

Docker и Docker Compose (рекомендуемый способ запуска всей системы)
```

## Запуск всех сервисов через Docker (Рекомендуемый способ)

```bash
# 1. Клонировать репозиторий
git clone https://github.com/Mishanyyya/PSWCS.git
cd PSWCS

# 2. Запустить все сервисы
docker-compose up --build

# Сервисы будут доступны:
# users: http://localhost:8001
# review: http://localhost:8002
# university: http://localhost:8003

# Остановка:
docker-compose down

# Удаление данных:
docker-compose down -v
```

## Локальный запуск

```bash
cd services/review
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

## Примеры API

### 1. Users (8001)

```bash
curl -X POST http://localhost:8001/users/ \
-H "Content-Type: application/json" \
-d '{"email":"student@example.com","password":"securepassword123","full_name":"Иван Петров"}'
```

```json
{
  "id": 1,
  "email": "student@example.com",
  "role": "user",
  "full_name": "Иван Петров"
}
```

### Login:

```bash
curl -X POST http://localhost:8001/users/login \
-H "Content-Type: application/json" \
-d '{"email":"student@example.com","password":"securepassword123"}'
```

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

### 2. Review (8002)

```bash
curl -X POST http://localhost:8002/api/v1/reviews/ \
-H "Authorization: Bearer <token>" \
-H "Content-Type: application/json" \
-d '{"university_id":1,"rating":5,"title":"Лучший университет!","body":"Учился здесь 4 года...","is_anonymous":false}'
```

```json
{
  "id": 1,
  "status": "pending",
  "author_id": 1
}
```

### Moderation:

```bash
curl -X POST http://localhost:8002/api/v1/reviews/1/approve \
-H "Authorization: Bearer <admin_token>"
```

```bash
curl -X POST http://localhost:8002/api/v1/reviews/1/reject \
-H "Authorization: Bearer <admin_token>" \
-H "Content-Type: application/json" \
-d '{"reason":"Нарушение правил"}'
```

### 3. University (8003)

```bash
curl http://localhost:8003/api/v1/universities
```

```json
[
  {
    "id": 1,
    "name": "МГУ им. М.В. Ломоносова",
    "city": "Москва",
    "review_count": 128,
    "avg_rating": 4.7
  }
]
```

## 🧪 Тестирование

```bash
cd services/review
pytest tests/ -v
```

## 🛡️ Безопасность

* bcrypt
* JWT
* Pydantic validation
* RBAC
* защита от дублей
* логирование

## 👥 Команда

* users — Mishanyyya
* review — f3n0men
* university — DaniilYakovlev-Rbk

## 📄 Лицензия

Нет информации — по умолчанию права защищены. Свяжитесь с авторами для уточнения условий использования.
