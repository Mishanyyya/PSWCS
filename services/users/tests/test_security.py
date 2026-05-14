"""
Тесты модуля безопасности: хэширование паролей и JWT.
"""
import time
import pytest
from unittest.mock import patch
from datetime import timedelta

from app.core.security import hash_password, verify_password, create_access_token


class TestHashPassword:
    def test_returns_string(self):
        result = hash_password("mypassword")
        assert isinstance(result, str)

    def test_hash_differs_from_plain(self):
        password = "mysecret"
        assert hash_password(password) != password

    def test_different_hashes_for_same_password(self):
        """bcrypt использует случайную соль — хэши должны различаться."""
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2

    def test_truncates_at_72_bytes(self):
        """Пароли длиннее 72 байт усекаются одинаково."""
        long_pass = "a" * 100
        h = hash_password(long_pass)
        assert verify_password("a" * 72, h)


class TestVerifyPassword:
    def test_correct_password(self):
        h = hash_password("correct")
        assert verify_password("correct", h) is True

    def test_wrong_password(self):
        h = hash_password("correct")
        assert verify_password("wrong", h) is False

    def test_empty_password_rejected(self):
        h = hash_password("notempty")
        assert verify_password("", h) is False

    def test_invalid_hash_returns_false(self):
        """Не должно падать на невалидном хэше."""
        assert verify_password("password", "not-a-bcrypt-hash") is False


class TestCreateAccessToken:
    def test_returns_string(self):
        token = create_access_token("42")
        assert isinstance(token, str)

    def test_token_contains_subject(self):
        from jose import jwt
        token = create_access_token("99")
        payload = jwt.decode(token, "test-secret-key", algorithms=["HS256"])
        assert payload["sub"] == "99"

    def test_token_has_expiry(self):
        from jose import jwt
        token = create_access_token("1")
        payload = jwt.decode(token, "test-secret-key", algorithms=["HS256"])
        assert "exp" in payload

    def test_token_expires_after_configured_time(self):
        from jose import jwt
        token = create_access_token("5")
        payload = jwt.decode(token, "test-secret-key", algorithms=["HS256"])
        # exp должен быть примерно через 30 минут
        expected = time.time() + 30 * 60
        assert abs(payload["exp"] - expected) < 5  # погрешность 5 секунд
