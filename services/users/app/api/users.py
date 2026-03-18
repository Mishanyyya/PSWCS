from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from jose import jwt, JWTError

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.services.user_service import create_user, get_user_by_email

router = APIRouter()


# --- Dependency ---
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# --- CREATE user ---
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, не существует ли уже пользователь с таким email
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return await create_user(db, user)


# --- LOGIN ---
@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email(db, data.email)
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}


# --- VALIDATE TOKEN (для других микросервисов) ---
@router.get("/auth/validation")
async def validate_token(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
):
    """
    Валидация JWT токена для других микросервисов
    Ожидает заголовок: "Bearer <token>"
    """
    # Проверяем наличие заголовка
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    # Проверяем формат заголовка
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Expected 'Bearer <token>'"
        )
    
    # Извлекаем токен
    token = authorization.replace("Bearer ", "")
    
    try:
        # Декодируем и проверяем токен
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=["HS256"]
        )
        
        # Извлекаем user_id из токена
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user ID"
            )
        
        # Проверяем что пользователь всё ещё существует в БД
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or deactivated"
            )
        
        # Возвращаем информацию о пользователе для других сервисов
        return {
            "valid": True,
            "user_id": user.id,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
            "expires_at": payload.get("exp")
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


# --- READ all users ---
@router.get("/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(User).offset(skip).limit(limit)
    )
    users = result.scalars().all()
    return users


# --- READ single user ---
@router.get("/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
    return user


# --- UPDATE user ---
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, 
    updated_user: UserCreate, 
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    # Проверяем, не занят ли email другим пользователем
    if updated_user.email != user.email:
        email_check = await db.execute(
            select(User).where(User.email == updated_user.email)
        )
        existing_user = email_check.scalar_one_or_none()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    user.email = updated_user.email
    user.full_name = updated_user.full_name
    
    # Обновляем пароль только если он предоставлен
    if updated_user.password:
        user.hashed_password = hash_password(updated_user.password)

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )

    await db.delete(user)
    await db.commit()
    return None