from fastapi import FastAPI
import uvicorn
from app.api.routers.university_routers import router as university_router  
from app.logger.logger import logger

def get_application() -> FastAPI:
    application = FastAPI(title="University service")
    application.include_router(router=university_router)
    return application

app = get_application()

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "API is running"}

if __name__ == "__main__":
    logger.info(f"Запуск приложения на порту 8003")
    uvicorn.run("main:app",
                port=8003,
                reload=True)