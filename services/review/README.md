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

## Структура
```
services/review/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── dependencies.py
│   ├── clients/          
│   ├── routers/          
│   └── seeds/           
├── .env.example
├── requirements.txt
├── Makefile
└── README.md
