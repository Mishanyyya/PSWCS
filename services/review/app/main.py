from dotenv import load_dotenv
from fastapi import FastAPI

from app.config import settings
from app.routers import moderation, reviews


load_dotenv()
app = FastAPI(title="Review Service", version="1.0.0", description="Сервис для управления отзывами на университеты")

# Подключаем роутеры
app.include_router(reviews.router)
app.include_router(moderation.router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.SERVICE_PORT)
