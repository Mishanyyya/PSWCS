from pydantic import BaseModel 
from typing import Optional

class UniversityBase(BaseModel):
    name: str
    city: str
    description: Optional[str] = None
    has_dormitory: bool = True
    website: Optional[str] = None

class UniversityRead(UniversityBase):
    id: int
    rating: float
    reviews_count: int
