from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import reviews, moderation
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="Review Service", 
    version="1.0.0",
    description="Сервис для управления отзывами на университеты"
)

# Подключаем роутеры
app.include_router(reviews.router)
app.include_router(moderation.router)

@app.on_event("startup")
async def startup():
    # Создание таблиц (только для разработки!)
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    print("Review service started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)