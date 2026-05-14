from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models import Review
from app.schemas import ReviewCreate, ReviewListResponse, ReviewResponse, ReviewUpdate
from app.clients.university_client import university_client 


router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewResponse, status_code=201)
async def create_review(
    review: ReviewCreate, 
    current_user: dict = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):

    
    #  существует ли уник
    university_exists = await university_client.check_university_exists(review.university_id)
    if not university_exists:
        raise HTTPException(
            status_code=404, 
            detail=f"University with id {review.university_id} not found"
        )
    
    # проверка на дубли
    existing = await db.execute(
        select(Review).where(
            Review.university_id == review.university_id,
            Review.author_id == current_user["user_id"]
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You have already reviewed this university")

    # Создаем
    db_review = Review(
        author_id=current_user["user_id"],
        **review.model_dump()
    )
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    
    # тбновляем статистику в university сервисе (если отзыв approved)
    # если статус pending позже при модерации
    if db_review.status == "approved":
        await university_client.update_stats(
            university_id=db_review.university_id, 
            rating=db_review.rating, 
            action="approve"
        )
    
    return db_review


@router.get("/my", response_model=ReviewListResponse)
async def get_my_reviews(
    current_user: dict = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(pending|approved|rejected)$"),
    db: AsyncSession = Depends(get_db),
):
    # Получение отзывов текущего пользователя
    query = select(Review).where(Review.author_id == current_user["user_id"])

    if status:
        query = query.where(Review.status == status)

    query = query.order_by(Review.created_at.desc())

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    reviews = result.scalars().all()

    return ReviewListResponse(data=reviews, total=total or 0, page=page, page_size=page_size)


@router.get("/university/{university_id}", response_model=ReviewListResponse)
async def get_university_reviews(
    university_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None, pattern="^(pending|approved|rejected)$"),
    sort_by: str = Query("created_at", pattern="^(created_at|rating)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    # Получение отзывов по университету

    query = select(Review).where(Review.university_id == university_id)

    if status:
        query = query.where(Review.status == status)
    else:
        query = query.where(Review.status == "approved")

    order_column = getattr(Review, sort_by)
    if sort_order == "desc":
        query = query.order_by(order_column.desc())
    else:
        query = query.order_by(order_column.asc())

    total = await db.scalar(select(func.count()).select_from(query.subquery()))
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    reviews = result.scalars().all()

    return ReviewListResponse(data=reviews, total=total or 0, page=page, page_size=page_size)


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: int,
    db: AsyncSession = Depends(get_db)
):
    # Получение отзыва по ID
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review




from app.models import Review, ModerationLog 
from sqlalchemy import delete
@router.delete("/{review_id}", status_code=204)
async def delete_review(
    review_id: int,
    current_user: dict = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    # Удаление отзыва (автор или админ)
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    is_author = review.author_id == current_user["user_id"]
    is_admin = current_user.get("role") == "admin"

    if not (is_author or is_admin):
        raise HTTPException(status_code=403, detail="Only author or admin can delete this review")

    # Сохраняем данные перед удалением для обновления статистики
    university_id = review.university_id
    rating = review.rating
    was_approved = review.status == "approved"
    
    #сначала удаляем связанные логи модерации
    await db.execute(
        delete(ModerationLog).where(ModerationLog.review_id == review_id)
    )
    
    # Теперь удаляем сам отзыв
    await db.delete(review)
    await db.commit()
    
    # Если удалили одобренный отзыв, обновляем статистику
    if was_approved:
        await university_client.update_stats(
            university_id=university_id,
            rating=rating,
            action="delete"
        )