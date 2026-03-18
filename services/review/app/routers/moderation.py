from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID
from datetime import datetime

from app.models import Review, ModerationLog
from app.schemas import ModerationReject, ModerationResponse, ModerationLogResponse, ReviewResponse 
from app.dependencies import get_db, get_current_admin
from app.clients.university_client import university_client

router = APIRouter(prefix="/api/v1/reviews", tags=["moderation"])

@router.get("/moderation/pending", response_model=list[ReviewResponse])
async def get_pending_reviews(
    admin: dict = Depends(get_current_admin),  # админ, не модератор
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Получение отзывов на модерацию (только для админов)"""
    query = select(Review).where(Review.status == "pending")
    query = query.order_by(Review.created_at.asc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/{review_id}/approve", response_model=ModerationResponse)
async def approve_review(
    review_id: UUID,
    admin: dict = Depends(get_current_admin),  # админ
    db: AsyncSession = Depends(get_db)
):
    """Одобрение отзыва (только для админов)"""
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review.status != "pending":
        raise HTTPException(status_code=400, detail=f"Review is already {review.status}")
    
    # Обновляем статус
    review.status = "approved"
    review.updated_at = datetime.utcnow()
    
    # Логируем действие
    log = ModerationLog(
        review_id=review_id,
        moderator_id=UUID(admin["user_id"]),  # moderator_id = admin_id
        action="approve"
    )
    db.add(log)
    
    await db.commit()

    # Уведомляем University service (отзыв теперь виден в статистике)
    await university_client.update_stats(
        university_id=review.university_id,
        rating=review.rating,
        action="approve"
    )
    
    return ModerationResponse(review_id=review_id, status="approved")

@router.post("/{review_id}/reject", response_model=ModerationResponse)
async def reject_review(
    review_id: UUID,
    rejection: ModerationReject,
    admin: dict = Depends(get_current_admin),  # админ
    db: AsyncSession = Depends(get_db)
):
    """Отклонение отзыва с причиной (только для админов)"""
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    if review.status != "pending":
        raise HTTPException(status_code=400, detail=f"Review is already {review.status}")
    
    # Обновляем статус
    review.status = "rejected"
    review.updated_at = datetime.utcnow()
    
    # Логируем действие
    log = ModerationLog(
        review_id=review_id,
        moderator_id=UUID(admin["user_id"]),
        action="reject",
        reason=rejection.reason
    )
    db.add(log)
    
    await db.commit()
    
    return ModerationResponse(review_id=review_id, status="rejected")

@router.get("/{review_id}/logs", response_model=list[ModerationLogResponse])
async def get_moderation_logs(
    review_id: UUID,
    admin: dict = Depends(get_current_admin),  # админ
    db: AsyncSession = Depends(get_db)
):
    """Получение логов модерации (только для админов)"""
    result = await db.execute(
        select(ModerationLog)
        .where(ModerationLog.review_id == review_id)
        .order_by(ModerationLog.created_at.desc())
    )
    return result.scalars().all()