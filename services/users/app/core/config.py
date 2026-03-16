from pydantic import BaseSettings


class Settings(BaseSettings):

    database_url: str
    jwt_secret: str
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"


settings = Settings()