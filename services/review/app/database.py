from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://postgres:pass@localhost:5432/review_db"

engine = create_async_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass