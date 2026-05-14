# Review Service

Сервис для управления отзывами на университеты.

---

## Начало работы

```bash
cd PSWCS/services/review

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Установить зависимости
make install

# Создать базу данных (PostgreSQL)
psql -U postgres -c "CREATE DATABASE reviews_db;"

# Cоздать таблицы
python -c "import asyncio; from app.database import engine; from app import models; asyncio.run(engine.run_sync(models.Base.metadata.create_all))"

# Настроить env по env.examples

# Заполнить тестовыми данными
make seed

# Запустить сервис
make run         
```
---
 
## Запуск через Docker (весь проект)
 
```bash
# Из корня репозитория
docker-compose up --build
 
# Остановить
docker-compose down
 
# Остановить и удалить данные БД
docker-compose down -v
```
 
Сервисы после запуска:
- http://localhost:8001 — User service
- http://localhost:8002 — Review service
- http://localhost:8003 — University service
---
 
## Тесты
 
```bash
pip install pytest pytest-asyncio httpx aiosqlite
 
pytest tests/ -v                        # все тесты
pytest tests/test_reviews.py -v         # только отзывы
pytest tests/test_moderation.py -v      # только модерация
pytest tests/test_clients.py -v         # только клиенты
```
 ## Примеры запросов
 
### Получить отзывы университета
 
```bash
curl http://localhost:8002/api/v1/reviews/university/1
```
```json
{
  "data": [{"id": 1, "university_id": 1, "rating": 4, "status": "approved", ...}],
  "total": 1, "page": 1, "page_size": 10
}
```
 
### Создать отзыв
 
```bash
curl -X POST http://localhost:8002/api/v1/reviews/ \
  -H "Authorization: Bearer <токен>" \
  -H "Content-Type: application/json" \
  -d '{"university_id": 1, "rating": 4, "title": "Хороший вуз",
       "body": "Учился четыре года, доволен качеством образования.", "is_anonymous": false}'
```
```json
{"id": 1, "status": "pending", ...}
```
 


---
 
## Структура проекта
 
```
services/review/
├── app/
│   ├── clients/
│   │   ├── university_client.py
│   │   └── user_client.py
│   ├── routers/
│   │   ├── reviews.py
│   │   └── moderation.py
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
├── migrations/
├── tests/
│   ├── conftest.py
│   ├── test_reviews.py
│   ├── test_moderation.py
│   └── test_clients.py
├── .env
├── alembic.ini
├── Dockerfile
└── requirements.txt
```