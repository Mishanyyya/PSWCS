
# Тесты create_user, get_user_by_email, get_user_by_id.

import pytest
import pytest_asyncio

from app.schemas.user import UserCreate
from app.services.user_service import create_user, get_user_by_email, get_user_by_id


@pytest.mark.asyncio
class TestCreateUser:
    async def test_creates_user_with_correct_fields(self, db_session):
        data = UserCreate(email="alice@example.com", password="pass123", full_name="Alice")
        user = await create_user(db_session, data)

        assert user.id is not None
        assert user.email == "alice@example.com"
        assert user.full_name == "Alice"
        assert user.role == "user"

    async def test_password_is_hashed(self, db_session):
        data = UserCreate(email="bob@example.com", password="plaintext")
        user = await create_user(db_session, data)

        assert user.hashed_password != "plaintext"
        assert len(user.hashed_password) > 20  #  хэш длинный

    async def test_default_role_is_user(self, db_session):
        data = UserCreate(email="carol@example.com", password="qwerty")
        user = await create_user(db_session, data)
        assert user.role == "user"

    async def test_full_name_optional(self, db_session):
        data = UserCreate(email="noname@example.com", password="pass")
        user = await create_user(db_session, data)
        assert user.full_name is None


@pytest.mark.asyncio
class TestGetUserByEmail:
    async def test_returns_existing_user(self, db_session):
        data = UserCreate(email="dave@example.com", password="pw")
        await create_user(db_session, data)

        found = await get_user_by_email(db_session, "dave@example.com")
        assert found is not None
        assert found.email == "dave@example.com"

    async def test_returns_none_for_unknown_email(self, db_session):
        result = await get_user_by_email(db_session, "ghost@example.com")
        assert result is None

    async def test_case_sensitive_email(self, db_session):
        data = UserCreate(email="eve@example.com", password="pw")
        await create_user(db_session, data)

        result = await get_user_by_email(db_session, "EVE@example.com")
        assert result is None 


@pytest.mark.asyncio
class TestGetUserById:
    async def test_returns_existing_user(self, db_session):
        data = UserCreate(email="frank@example.com", password="pw")
        created = await create_user(db_session, data)

        found = await get_user_by_id(db_session, created.id)
        assert found is not None
        assert found.id == created.id

    async def test_returns_none_for_invalid_id(self, db_session):
        result = await get_user_by_id(db_session, 99999)
        assert result is None
