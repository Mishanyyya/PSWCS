from pydantic import BaseModel, Field
from typing import Optional

class UniversityBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Название ВУЗа")
    city: str = Field(..., min_length=2, max_length=100, description="Город расположения")
    description: Optional[str] = Field(None, description="Описание инфраструктуры и программ")
    has_dormitory: bool = Field(default=True, description="Наличие общежития")
    website: Optional[str] = Field(None, max_length=255, description="Ссылка на официальный сайт")

class UniversityCreate(UniversityBase):
    pass

class UniversityRead(UniversityBase):
    id: int
    rating: float = Field(..., ge=0, le=5)
    reviews_count: int = Field(..., ge=0)

    class Config:
        from_attributes = True

class UniversityRatingUpdate(BaseModel):
    new_score: float = Field(
        ..., 
        ge=1.0, 
        le=5.0, 
        description="Оценка от пользователя должна быть строго в диапазоне [1, 5]"
    ),
    action: str = "approve"

class UniversityUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    description: Optional[str] = None
    has_dormitory: Optional[bool] = None
    website: Optional[str] = None