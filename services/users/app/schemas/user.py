from typing import Optional

from pydantic import BaseModel, EmailStr


# --- CREATE ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


# --- LOGIN ---
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# --- RESPONSE ---
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    full_name: Optional[str] = None

    class Config:
        from_attributes = True
