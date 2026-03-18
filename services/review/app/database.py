from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "postgresql+asyncpg://postgres:pass@localhost:5432/review_db"

engine = create_async_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    """Генератор сессий для зависимостей FastAPI"""
    async with AsyncSessionLocal() as session:
        yield session