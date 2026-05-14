

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# мок сеттингов
mock_settings = MagicMock()
mock_settings.database_url = "sqlite+aiosqlite:///:memory:"
mock_settings.LOG_LEVEL = "INFO"

with patch("app.core.config.settings", mock_settings):
    pass 

# бд тестовая
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DB_URL, echo=False)
TestSession = async_sessionmaker(test_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


import app.db.database as db_module 
db_module.engine = test_engine
db_module.async_session_maker = TestSession


async def override_get_async_session():
    async with TestSession() as session:
        yield session


db_module.get_async_session = override_get_async_session

from app.models.university_model import University 
from app.main import app                          
from app.db.database import get_async_session       

app.dependency_overrides[get_async_session] = override_get_async_session


# создаем или удаляем таблицы для каждого теста
@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(University.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(University.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with TestSession() as session:
        yield session


# вставка напрямую в бд
async def make_university(
    db: AsyncSession,
    name: str = "МГУ",
    city: str = "Москва",
    description: str = "Главный университет страны",
    has_dormitory: bool = True,
    website: str = "https://msu.ru",
    rating: float = 0.0,
    reviews_count: int = 0,
) -> University:
    uni = University(
        name=name,
        city=city,
        description=description,
        has_dormitory=has_dormitory,
        website=website,
        rating=rating,
        reviews_count=reviews_count,
    )
    db.add(uni)
    await db.commit()
    await db.refresh(uni)
    return uni