
# Интеграционные тесты API-эндпоинтов микросервиса пользователей.

import pytest
from httpx import AsyncClient


REGISTER_URL = "/users/"
LOGIN_URL = "/users/login"
VALIDATE_URL = "/users/auth/validation"



async def register_user(client: AsyncClient, email="test@test.com", password="pass123", full_name="Test User"):
    return await client.post(REGISTER_URL, json={
        "email": email,
        "password": password,
        "full_name": full_name,
    })


async def get_token(client: AsyncClient, email="test@test.com", password="pass123") -> str:
    resp = await client.post(LOGIN_URL, json={"email": email, "password": password})
    return resp.json()["access_token"]

# регистрация

@pytest.mark.asyncio
class TestRegister:
    async def test_register_success(self, client):
        resp = await register_user(client)
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "test@test.com"
        assert body["role"] == "user"
        assert "id" in body
        assert "hashed_password" not in body  # пароль не утекает

    async def test_register_duplicate_email(self, client):
        await register_user(client)
        resp = await register_user(client)
        assert resp.status_code == 400
        assert "already registered" in resp.json()["detail"]

    async def test_register_invalid_email(self, client):
        resp = await client.post(REGISTER_URL, json={"email": "not-an-email", "password": "pw"})
        assert resp.status_code == 422

    async def test_register_missing_password(self, client):
        resp = await client.post(REGISTER_URL, json={"email": "x@x.com"})
        assert resp.status_code == 422

    async def test_register_without_full_name(self, client):
        resp = await client.post(REGISTER_URL, json={"email": "noname@test.com", "password": "pw"})
        assert resp.status_code == 201
        assert resp.json()["full_name"] is None


#  Логин 
@pytest.mark.asyncio
class TestLogin:
    async def test_login_success(self, client):
        await register_user(client)
        resp = await client.post(LOGIN_URL, json={"email": "test@test.com", "password": "pass123"})
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    async def test_login_wrong_password(self, client):
        await register_user(client)
        resp = await client.post(LOGIN_URL, json={"email": "test@test.com", "password": "wrong"})
        assert resp.status_code == 401

    async def test_login_unknown_email(self, client):
        resp = await client.post(LOGIN_URL, json={"email": "ghost@test.com", "password": "pw"})
        assert resp.status_code == 401

    async def test_login_invalid_payload(self, client):
        resp = await client.post(LOGIN_URL, json={"email": "not-email"})
        assert resp.status_code == 422

# валидация токена

@pytest.mark.asyncio
class TestValidateToken:
    async def test_valid_token(self, client):
        await register_user(client)
        token = await get_token(client)
        resp = await client.get(VALIDATE_URL, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["valid"] is True
        assert body["email"] == "test@test.com"
        assert "user_id" in body

    async def test_missing_header(self, client):
        resp = await client.get(VALIDATE_URL)
        assert resp.status_code == 401

    async def test_invalid_format(self, client):
        resp = await client.get(VALIDATE_URL, headers={"Authorization": "Token abc"})
        assert resp.status_code == 401

    async def test_garbage_token(self, client):
        resp = await client.get(VALIDATE_URL, headers={"Authorization": "Bearer garbage.token.here"})
        assert resp.status_code == 401

    async def test_expired_token(self, client):
        """Ручная генерация истёкшего токена."""
        from datetime import datetime
        from jose import jwt
        payload = {"sub": "1", "exp": datetime(2000, 1, 1)}
        expired = jwt.encode(payload, "test-secret-key", algorithm="HS256")
        resp = await client.get(VALIDATE_URL, headers={"Authorization": f"Bearer {expired}"})
        assert resp.status_code == 401


# круд пользователей

@pytest.mark.asyncio
class TestUserCRUD:
    async def test_get_all_users_empty(self, client):
        resp = await client.get(REGISTER_URL)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_get_all_users_after_register(self, client):
        await register_user(client, "a@a.com")
        await register_user(client, "b@b.com")
        resp = await client.get(REGISTER_URL)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    async def test_get_user_by_id(self, client):
        reg = await register_user(client)
        user_id = reg.json()["id"]
        resp = await client.get(f"/users/{user_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == user_id

    async def test_get_nonexistent_user(self, client):
        resp = await client.get("/users/99999")
        assert resp.status_code == 404

    async def test_update_user(self, client):
        reg = await register_user(client)
        user_id = reg.json()["id"]
        resp = await client.put(f"/users/{user_id}", json={
            "email": "updated@test.com",
            "password": "newpass",
            "full_name": "Updated Name",
        })
        assert resp.status_code == 200
        assert resp.json()["email"] == "updated@test.com"
        assert resp.json()["full_name"] == "Updated Name"

    async def test_update_to_duplicate_email(self, client):
        await register_user(client, "first@test.com")
        reg2 = await register_user(client, "second@test.com")
        user_id = reg2.json()["id"]
        resp = await client.put(f"/users/{user_id}", json={
            "email": "first@test.com",
            "password": "pw",
        })
        assert resp.status_code == 400

    async def test_delete_user(self, client):
        reg = await register_user(client)
        user_id = reg.json()["id"]
        resp = await client.delete(f"/users/{user_id}")
        assert resp.status_code == 204
        # Убеждаемся, что удалён
        get_resp = await client.get(f"/users/{user_id}")
        assert get_resp.status_code == 404

    async def test_delete_nonexistent_user(self, client):
        resp = await client.delete("/users/99999")
        assert resp.status_code == 404
