"""
тут как бы
роверяем что клиенты правильно обрабатывают ответы
внешних сервисов
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx


# юзер клиент
class TestUserClient:

    @pytest.mark.asyncio
    async def test_validate_token_success(self):
        # валидный токен возвращает данные юзера
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
        # невалидный (401) значит none
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
        # если сервис недоступен то none
        from app.clients.user_client import UserClient

        with patch("httpx.AsyncClient.get", side_effect=httpx.ConnectError("refused")):
            client = UserClient()
            result = await client.validate_token("any_token")

        assert result is None

    @pytest.mark.asyncio
    async def test_validate_token_unexpected_error(self):
        # любая непредвиденная ошибка тоже none
        from app.clients.user_client import UserClient

        with patch("httpx.AsyncClient.get", side_effect=Exception("unexpected")):
            client = UserClient()
            result = await client.validate_token("any_token")

        assert result is None

# юниверсити клиент
class TestUniversityClient:

    @pytest.mark.asyncio
    async def test_check_university_exists_true(self):
        # вернул 200 - тру
        from app.clients.university_client import UniversityClient

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            client = UniversityClient()
            result = await client.check_university_exists(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_check_university_exists_false(self):
        # вернул 404 - фолз
        from app.clients.university_client import UniversityClient

        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_response):
            client = UniversityClient()
            result = await client.check_university_exists(999)

        assert result is False

    @pytest.mark.asyncio
    async def test_check_university_service_down(self):
    #   недоступен значит тожеж фолз
        from app.clients.university_client import UniversityClient

        with patch("httpx.AsyncClient.get", side_effect=Exception("timeout")):
            client = UniversityClient()
            result = await client.check_university_exists(1)

        assert result is False

    @pytest.mark.asyncio
    async def test_update_stats_success(self):
        # обновили стату - тру
        from app.clients.university_client import UniversityClient

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.AsyncClient.patch", new_callable=AsyncMock, return_value=mock_response):
            client = UniversityClient()
            result = await client.update_stats(university_id=1, rating=4, action="approve")

        assert result is True

    @pytest.mark.asyncio
    async def test_update_stats_service_down(self):
        # недоступен когда стату обновляем - фолз
        from app.clients.university_client import UniversityClient

        with patch("httpx.AsyncClient.patch", side_effect=Exception("timeout")):
            client = UniversityClient()
            result = await client.update_stats(university_id=1, rating=4, action="approve")

        assert result is False