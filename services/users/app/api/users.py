from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.core.security import verify_password, create_access_token
from app.services.user_service import create_user, get_user_by_email

router = APIRouter()


# --- Dependency ---
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# --- CREATE user ---
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user)


# --- LOGIN ---
@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}


# --- READ all users ---
@router.get("/", response_model=List[UserResponse])
async def read_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


# --- READ single user ---
@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# --- UPDATE user ---
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, updated_user: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.email = updated_user.email
    user.full_name = updated_user.full_name
    # для пароля лучше через отдельный метод хеширования
    if updated_user.password:
        from app.core.security import get_password_hash
        user.hashed_password = get_password_hash(updated_user.password)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# --- DELETE user ---
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await db.delete(user)
    await db.commit()
    return None