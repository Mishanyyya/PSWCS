from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.services.user_service import create_user, get_user_by_email
from app.db.session import AsyncSessionLocal
from app.core.security import verify_password, create_access_token

router = APIRouter()


async def get_db():

    async with AsyncSessionLocal() as session:
        yield session


@router.post("/register", response_model=UserResponse)
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
):

    return await create_user(db, user)


@router.post("/login")
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
):

    user = await get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(status_code=401)

    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401)

    token = create_access_token(str(user.id))

    return {"access_token": token}