# app/config.py
import os

from dotenv import load_dotenv


# Загружаем .env файл
load_dotenv()


class Settings:
    # Настройки сервиса отзывов

    # Базовые настройки
    SERVICE_NAME: str = os.getenv("SERVICE_NAME", "reviews")
    SERVICE_PORT: int = int(os.getenv("SERVICE_PORT", "8002"))

    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Другие сервисы
    USERS_SERVICE_URL: str = os.getenv("USERS_SERVICE_URL", "http://localhost:8001")
    UNIVERSITY_SERVICE_URL: str = os.getenv("UNIVERSITY_SERVICE_URL", "http://localhost:8003")

    # Таймауты
    REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT", "10.0"))


# Создаем экземпляр настроек
settings = Settings()
