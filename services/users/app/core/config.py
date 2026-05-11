from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Users Service"

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    SQL_ECHO: bool = False
    DEFAULT_USER_ROLE: str = "user"

    SEED_ADMIN_EMAIL: Optional[str] = None
    SEED_ADMIN_PASSWORD: Optional[str] = None
    SEED_ADMIN_FULL_NAME: Optional[str] = None
    SEED_USER_ROLES: Optional[str] = None
    SEED_OUTPUT_FILE: Optional[str] = None

    HOST: str = "127.0.0.1"
    PORT: int = 8001

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()