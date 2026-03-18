from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime

class ReviewCreate(BaseModel):
    university_id: UUID
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
    id: UUID
    university_id: UUID
    author_id: UUID
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
    review_id: UUID
    status: str


class ModerationLogResponse(BaseModel):
    id: UUID
    review_id: UUID
    moderator_id: UUID
    action: str
    reason: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

class UniversityStatsResponse(BaseModel):
    university_id: UUID
    review_count: int
    avg_rating: float
    rating_distribution: dict[str, int]
