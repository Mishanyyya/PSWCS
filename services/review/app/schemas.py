from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    university_id: int 
    rating: int = Field(ge=1, le=5)
    title: str = Field(min_length=5, max_length=255)
    body: str = Field(min_length=50)
    is_anonymous: bool = False


class ReviewUpdate(BaseModel):
    rating: int | None = Field(None, ge=1, le=5)
    title: str | None = Field(None, min_length=5, max_length=255)
    body: str | None = Field(None, min_length=50)
    is_anonymous: bool | None = None


class ReviewResponse(BaseModel):
    id: int  
    university_id: int 
    author_id: int  
    rating: int
    title: str
    body: str
    status: str
    is_anonymous: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReviewListResponse(BaseModel):
    data: list[ReviewResponse]
    total: int
    page: int
    page_size: int


class ModerationReject(BaseModel):
    reason: str = Field(min_length=5)


class ModerationResponse(BaseModel):
    review_id: int 
    status: str


class ModerationLogResponse(BaseModel):
    id: int 
    review_id: int 
    moderator_id: int  
    action: str
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UniversityStatsResponse(BaseModel):
    university_id: int 
    review_count: int
    avg_rating: float
    rating_distribution: dict[str, int]