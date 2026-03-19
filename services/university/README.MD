# University Service API

## Описание

University Service API - это RESTful API сервис, разработанный с использованием FastAPI для управления информацией о университетах. Сервис предоставляет CRUD операции для работы с данными университетов.

## Функциональность

- **Получение списка всех университетов**: GET /universities/
- **Получение университета по ID**: GET /universities/{id}
- **Создание нового университета**: POST /universities/

## Технологии

- **FastAPI**: Веб-фреймворк для создания API
- **SQLAlchemy**: ORM для работы с базой данных
- **PostgreSQL**: Реляционная база данных
- **asyncpg**: Асинхронный драйвер PostgreSQL
- **Uvicorn**: ASGI сервер
- **Alembic**: Инструмент для миграций базы данных
- **Pydantic**: Валидация данных
- **Ruff**: Линтер и форматтер кода

## Структура проекта

```
university-service/
├── app/
│   ├── main.py                    # Точка входа приложения
│   ├── api/
│   │   ├── crud/
│   │   │   └── university_crud.py # CRUD операции
│   │   ├── routers/
│   │   │   └── university_routers.py # API роутеры
│   │   └── schemas/
│   │       └── university_schema.py # Pydantic схемы
│   ├── core/
│   │   └── config.py              # Конфигурация приложения
│   ├── db/
│   │   └── database.py            # Настройка базы данных
│   ├── errors/
│   │   └── exceptions.py          # Пользовательские исключения
│   ├── logger/
│   │   └── logger.py              # Настройка логирования
│   └── models/
│       └── university_model.py    # SQLAlchemy модели
├── migrations/                    # Alembic миграции
├── alembic.ini                    # Конфигурация Alembic
├── requirements.txt               # Основные зависимости
├── requirements-dev.txt           # Зависимости для разработки
└── README.md                      
```

## API Endpoints

### Получить все университеты
- **GET** `/universities/`
- **Ответ**: Список университетов

### Получить университет по ID
- **GET** `/universities/{id}`
- **Параметры**: `id` (integer) - ID университета
- **Ответ**: Данные университета или 404, если не найден

### Создать новый университет
- **POST** `/universities/`
- **Тело запроса**:
  ```json
  {
    "name": "Название университета",
    "city": "Город",
    "description": "Описание (опционально)",
    "has_dormitory": true,
    "website": "https://example.com (опционально)"
  }
  ```
- **Ответ**: Созданный университет или 409, если университет с таким названием уже существует

## Модель данных

### University
- `id`: integer (автоинкремент)
- `name`: string (название университета)
- `city`: string (город)
- `description`: string (описание, опционально)
- `rating`: float (рейтинг, по умолчанию 0.0)
- `reviews_count`: integer (количество отзывов, по умолчанию 0)
- `website`: string (сайт, опционально)
- `has_dormitory`: boolean (наличие общежития, по умолчанию true)

## Логирование

Логи записываются в файл `app/logger/app.log` и выводятся в консоль. Уровень логирования настраивается через переменную окружения `LOG_LEVEL`.