from app.api.users import router as users_router
from fastapi import FastAPI


app = FastAPI(title="Users Service")

app.include_router(users_router, prefix="/users", tags=["users"])
