from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.university_client import university_client
from app.dependencies import get_current_admin, get_db
from app.models import ModerationLog, Review
from app.schemas import ModerationLogResponse, ModerationReject, ModerationResponse, ReviewResponse


router = APIRouter(prefix="/api/v1/reviews", tags=["moderation"])


@router.get("/moderation/pending", response_model=list[ReviewResponse])
async def get_pending_reviews(
    admin: dict = Depends(get_current_admin),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    # Получение отзывов на модерацию (только для админов)
    query = select(Review).where(Review.status == "pending")
    query = query.order_by(Review.created_at.asc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/{review_id}/approve", response_model=ModerationResponse)
async def approve_review(
    review_id: int,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
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
        moderator_id=admin["user_id"],
        action="approve",
    )
    db.add(log)

    await db.commit()

    # Обновляем статистику в university сервисе
    try:
        await university_client.update_stats(
            university_id=review.university_id, 
            rating=review.rating, 
            action="approve"
        )
    except Exception as e:
        # Логируем ошибку, но не откатываем одобрение отзыва
        print(f"Failed to update university stats for ID {review.university_id}: {e}")

    return ModerationResponse(review_id=review_id, status="approved")


@router.post("/{review_id}/reject", response_model=ModerationResponse)
async def reject_review(
    review_id: int,
    rejection: ModerationReject,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    # Отклонение отзыва с причиной (только для админов)
    review = await db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review.status != "pending":
        raise HTTPException(status_code=400, detail=f"Review is already {review.status}")

    # Обновляем
    review.status = "rejected"
    review.updated_at = datetime.utcnow()

    # Логируем 
    log = ModerationLog(
        review_id=review_id,
        moderator_id=admin["user_id"],
        action="reject",
        reason=rejection.reason
    )
    db.add(log)

    await db.commit()

    # Для rejected отзывов не обновляем статистику

    return ModerationResponse(review_id=review_id, status="rejected")


@router.get("/{review_id}/logs", response_model=list[ModerationLogResponse])
async def get_moderation_logs(
    review_id: int,
    admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    # Получение логов модерации (только для админов)
    result = await db.execute(
        select(ModerationLog)
        .where(ModerationLog.review_id == review_id)
        .order_by(ModerationLog.created_at.desc())
    )
    return result.scalars().all()