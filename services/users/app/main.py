from app.api.users import router as users_router
from app.core.config import settings
from fastapi import FastAPI


app = FastAPI(title=settings.APP_NAME)

app.include_router(users_router, prefix="/users", tags=["users"])
