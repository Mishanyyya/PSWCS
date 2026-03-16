from pydantic import BaseModel, EmailStr
from uuid import UUID


class UserCreate(BaseModel):

    email: EmailStr
    username: str
    password: str


class UserLogin(BaseModel):

    email: EmailStr
    password: str


class UserResponse(BaseModel):

    id: UUID
    email: EmailStr
    username: str

    class Config:
        from_attributes = True