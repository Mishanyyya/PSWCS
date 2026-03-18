from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional
from datetime import datetime

from app.models import Review
from app.schemas import ReviewCreate, ReviewUpdate, ReviewResponse, ReviewListResponse
from app.dependencies import get_db, get_current_user, get_current_admin

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])

@router.post("/", response_model=ReviewResponse, status_code=201)
async def create_review(
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Создание нового отзыва"""
    # Проверка на дубликат (один отзыв на пользователя на вуз)
    existing = await db.execute(
        select(Review).where(
            Review.university_id == review.university_id,
            Review.author_id == UUID(current_user["user_id"])
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=400, 
            detail="You have already reviewed this university"
        )
    
    # Создание отзыва
    db_review = Review(
        author_id=UUID(current_user["user_id"]),
        **review.model_dump() 
)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Получение отзыва по ID"""
    result = await db.execute(
        select(Review).where(Review.id == review_id)
    )
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.get("/university/{university_id}", response_model=ReviewListResponse)
async def get_university_reviews(
    university_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(pending|approved|rejected)$"),
    sort_by: str = Query("created_at", pattern="^(created_at|rating)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db)
):
    """Получение отзывов по университету"""
    # Базовый запрос
    query = select(Review).where(Review.university_id == university_id)
    
    # Фильтр по статусу (по умолчанию только approved для публичного доступа)
    if status:
        query = query.where(Review.status == status)
    else:
        query = query.where(Review.status == "approved")
    
    # Сортировка
    order_column = getattr(Review, sort_by)
    if sort_order == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())
    
    # Пагинация
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return ReviewListResponse(
        data=reviews,
        total=total or 0,
        page=page,
        page_size=page_size
    )


@router.get("/my", response_model=ReviewListResponse)
async def get_my_reviews(
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(pending|approved|rejected)$"),
    db: AsyncSession = Depends(get_db)
):
    """Получение отзывов текущего пользователя"""
    query = select(Review).where(Review.author_id == UUID(current_user["user_id"]))
    
    if status:
        query = query.where(Review.status == status)
    
    query = query.order_by(Review.created_at.desc())
    
    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    reviews = result.scalars().all()
    
    return ReviewListResponse(
        data=reviews,
        total=total or 0,
        page=page,
        page_size=page_size
    )


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: UUID,
    review_update: ReviewUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновление отзыва (только автор, пока отзыв в статусе pending)"""
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Только автор может обновлять
    if str(review.author_id) != current_user["user_id"]:
        raise HTTPException(
            status_code=403, 
            detail="Only author can update this review"
        )
    
    # Нельзя редактировать после модерации
    if review.status != "pending":
        raise HTTPException(
            status_code=400, 
            detail="Cannot edit review after moderation"
        )
    
    # Обновляем только переданные поля
    update_data = review_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    review.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Удаление отзыва (автор или админ)"""
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Проверка прав: автор ИЛИ админ
    is_author = str(review.author_id) == current_user["user_id"]
    is_admin = current_user.get("role") == "admin"
    
    if not (is_author or is_admin):
        raise HTTPException(
            status_code=403, 
            detail="Only author or admin can delete this review"
        )
    
    await db.delete(review)
    await db.commit()