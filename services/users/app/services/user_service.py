from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    """
    Создание нового пользователя
    """
    new_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hash_password(user.password),
        role="user"  # роль по умолчанию
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Получение пользователя по email
    """
    result = await db.execute(
        select(User).where(User.email == email)
    )
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Получение пользователя по ID (понадобится для валидации токена)
    """
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()