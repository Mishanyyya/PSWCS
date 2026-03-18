from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_session
from app.clients.user_client import user_client

security = HTTPBearer()

async def get_db() -> AsyncSession:
    """Зависимость для получения сессии БД"""
    async for session in get_session():
        yield session

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Проверяет токен через User service и возвращает данные пользователя
    Используется во всех защищенных эндпоинтах
    """
    token = credentials.credentials
    user_data = await user_client.validate_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Преобразуем user_id в UUID для удобства
    user_data["user_id"] = UUID(user_data["user_id"])
    return user_data

async def get_current_admin(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Проверяет, что пользователь является администратором
    Используется для эндпоинтов модерации
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

# Алиас для понятности
get_current_moderator = get_current_admin