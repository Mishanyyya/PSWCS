import uuid
from sqlalchemy import Integer, String, Float, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs

class Base(AsyncAttrs, DeclarativeBase):
    __abstract__ = True     

class University(Base):
    __tablename__ = 'universities'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100)) 
    description: Mapped[str] = mapped_column(Text, nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0) 
    reviews_count: Mapped[int] = mapped_column(Integer, default=0)
    website: Mapped[str] = mapped_column(String(255), nullable=True)
    has_dormitory: Mapped[bool] = mapped_column(Boolean, default=True)