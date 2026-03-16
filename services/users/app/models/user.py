import enum

from app.db.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy import Enum as SQLEnum


class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(
        SQLEnum(UserRole, name="user_role"),  # имя для PostgreSQL
        nullable=False,
        default=UserRole.user
    )
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
