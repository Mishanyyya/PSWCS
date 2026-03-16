from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


async def create_user(db: AsyncSession, user: UserCreate):

    new_user = User(
        email=user.email,
        username=user.username,
        password_hash=hash_password(user.password),
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)

    return new_user


async def get_user_by_email(db: AsyncSession, email: str):

    result = await db.execute(
        select(User).where(User.email == email)
    )

    return result.scalar_one_or_none()