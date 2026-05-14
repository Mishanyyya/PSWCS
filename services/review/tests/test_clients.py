"""
test_clients.py — тесты для межсервисных клиентов

Проверяем что клиенты правильно обрабатывают ответы
внешних сервисов и не падают при их недоступности.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx


# ══════════════════════════════════════════════════════════════════════════════
# UserClient
# ══════════════════════════════════════════════════════════════════════════════
class TestUserClient:

    @pytest.mark.asyncio
    async def test_validate_token_success(self):
        """Валидный токен → возвращает данные пользователя."""
        from app.clients.user_client import UserClient

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user_id": 1,
            "role": "user",
            "email": "test@test.com"
        }
        mock_response.text = '{"user_id": 1, "role": "user"}'

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            client = UserClient()
            result = await client.validate_token("valid_token")

        assert result is not None
        assert result["user_id"] == 1
        assert result["role"] == "user"

    @pytest.mark.asyncio
    async def test_validate_token_invalid(self):
        """Невалидный токен (401 от сервиса) → None."""
        from app.clients.user_client import UserClient

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            client = UserClient()
            result = await client.validate_token("bad_token")

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_token_service_unavailable(self):
        """User service недоступен → None (не исключение)."""
        from app.clients.user_client import UserClient

        with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("refused")):
            client = UserClient()
            result = await client.validate_token("any_token")

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_token_unexpected_error(self):
        """Непредвиденная ошибка → None (не падает)."""
        from app.clients.user_client import UserClient

        with patch("httpx.AsyncClient.get", side_effect=Exception("unexpected")):
            client = UserClient()
            result = await client.validate_token("any_token")

        assert result is None


# ══════════════════════════════════════════════════════════════════════════════
# UniversityClient
# ══════════════════════════════════════════════════════════════════════════════
class TestUniversityClient:

    @pytest.mark.asyncio
    async def test_check_university_exists_true(self):
        """University service вернул 200 → True."""
        from app.clients.university_client import UniversityClient

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            client = UniversityClient()
            result = await client.check_university_exists(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_check_university_exists_false(self):
        """University service вернул 404 → False."""
        from app.clients.university_client import UniversityClient

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            client = UniversityClient()
            result = await client.check_university_exists(999)

        assert result is False

    @pytest.mark.asyncio
    async def test_check_university_service_down(self):
        """University service недоступен → False (не исключение)."""
        from app.clients.university_client import UniversityClient

        with patch("httpx.AsyncClient.get", side_effect=Exception("timeout")):
            client = UniversityClient()
            result = await client.check_university_exists(1)

        assert result is False

    @pytest.mark.asyncio
    async def test_update_stats_success(self):
        """Успешное обновление статистики → True."""
        from app.clients.university_client import UniversityClient

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient.patch", new_callable=AsyncMock, return_value=mock_response):
            client = UniversityClient()
            result = await client.update_stats(university_id=1, rating=4, action="approve")

        assert result is True

    @pytest.mark.asyncio
    async def test_update_stats_service_down(self):
        """University service недоступен при update_stats → False (не падает)."""
        from app.clients.university_client import UniversityClient

        with patch("httpx.AsyncClient.patch", side_effect=Exception("timeout")):
            client = UniversityClient()
            result = await client.update_stats(university_id=1, rating=4, action="approve")

        assert result is False