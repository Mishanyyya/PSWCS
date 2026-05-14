"""
Используем SQLite in-memory вместо реального PostgreSQL,
чтобы тесты работали без запущенных сервисов.
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass
import app.database as db_module
db_module.Base = Base
db_module.engine = test_engine
db_module.AsyncSessionLocal = TestSessionLocal

from app.models import Review, ModerationLog 
from app.main import app                       
from app.dependencies import get_db       


# переопределяем зависимости бд
async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db


# таблицы вокруг каждого теста 
@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# прямая сессия бд чтоб данные подготовить
@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with TestSessionLocal() as session:
        yield session

 
REGULAR_USER = {"user_id": 1, "role": "user",  "email": "user@test.com"}
ADMIN_USER   = {"user_id": 2, "role": "admin", "email": "admin@test.com"}
OTHER_USER   = {"user_id": 3, "role": "user",  "email": "other@test.com"}

AUTH = {"Authorization": "Bearer faketoken"}  


# моки
@pytest.fixture
def mock_as_regular_user():
    with patch("app.clients.user_client.user_client.validate_token", new_callable=AsyncMock) as m:
        m.return_value = REGULAR_USER
        yield m

@pytest.fixture
def mock_as_admin():
    with patch("app.clients.user_client.user_client.validate_token", new_callable=AsyncMock) as m:
        m.return_value = ADMIN_USER
        yield m

@pytest.fixture
def mock_as_other_user():
    with patch("app.clients.user_client.user_client.validate_token", new_callable=AsyncMock) as m:
        m.return_value = OTHER_USER
        yield m

@pytest.fixture
def mock_as_unauth():
    with patch("app.clients.user_client.user_client.validate_token", new_callable=AsyncMock) as m:
        m.return_value = None
        yield m

# юниверсити моки
@pytest.fixture
def university_exists():
    with patch("app.clients.university_client.university_client.check_university_exists",
               new_callable=AsyncMock) as m:
        m.return_value = True
        yield m

@pytest.fixture
def university_not_exists():
    with patch("app.clients.university_client.university_client.check_university_exists",
               new_callable=AsyncMock) as m:
        m.return_value = False
        yield m

@pytest.fixture
def university_update_stats():
    with patch("app.clients.university_client.university_client.update_stats",
               new_callable=AsyncMock) as m:
        m.return_value = True
        yield m


# вспомогательная чтоб отзыв прям в бд вставитьь
async def make_review(
    db: AsyncSession,
    university_id: int = 1,
    author_id: int = 1,
    rating: int = 4,
    title: str = "Тестовый отзыв",
    body: str = "Достаточно длинный текст отзыва для прохождения валидации в пятьдесят символов.",
    status: str = "pending",
    is_anonymous: bool = False,
) -> Review:
    review = Review(
        university_id=university_id,
        author_id=author_id,
        rating=rating,
        title=title,
        body=body,
        status=status,
        is_anonymous=is_anonymous,
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)
    return review