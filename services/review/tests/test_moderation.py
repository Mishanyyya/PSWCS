"""
модерация с учётом ролей из User service.
Обычный пользователь не может модерировать 
"""
import pytest
from conftest import make_review, REGULAR_USER, ADMIN_USER, AUTH



# GET /api/v1/reviews/moderation/pending 
class TestModerationQueue:

    @pytest.mark.asyncio
    async def test_admin_sees_pending_reviews(self, client, db_session, mock_as_admin):
    #    адимн получает все ревью в статусе пендинг
        await make_review(db_session, status="pending")
        await make_review(db_session, author_id=99, university_id=2, status="pending")
        await make_review(db_session, author_id=88, university_id=3, status="approved")  # не должен попасть

        resp = await client.get("/api/v1/reviews/moderation/pending", headers=AUTH)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert all(r["status"] == "pending" for r in data)

    @pytest.mark.asyncio
    async def test_regular_user_forbidden(self, client, db_session, mock_as_regular_user):
        # для обычного у нас будет 403 (он не должен видеть)
        resp = await client.get("/api/v1/reviews/moderation/pending", headers=AUTH)
        assert resp.status_code == 403

    @pytest.mark.asyncio
    async def test_unauthenticated_forbidden(self, client, mock_as_unauth):
    # без токена 401  
        resp = await client.get("/api/v1/reviews/moderation/pending", headers=AUTH)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_empty_queue(self, client, mock_as_admin):
        # очереди нет - пустой список и всё
        resp = await client.get("/api/v1/reviews/moderation/pending", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_pagination(self, client, db_session, mock_as_admin):
        # разбивка на страницы
        for i in range(5):
            await make_review(db_session, author_id=100 + i, university_id=i + 1, status="pending")

        resp = await client.get("/api/v1/reviews/moderation/pending?page=1&page_size=2", headers=AUTH)
        assert resp.status_code == 200
        assert len(resp.json()) == 2


# POST /api/v1/reviews/{id}/approve 
class TestApproveReview:

    @pytest.mark.asyncio
    async def test_admin_approves_pending(
        self, client, db_session, mock_as_admin, university_update_stats
    ):
        # одобрение - смена пендинг на апрув
        review = await make_review(db_session, status="pending")
        resp = await client.post(f"/api/v1/reviews/{review.id}/approve", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["status"] == "approved"

    @pytest.mark.asyncio
    async def test_approve_calls_university_stats(
        self, client, db_session, mock_as_admin, university_update_stats
    ):
    #    обновление статистики идет после апрув
        review = await make_review(db_session, status="pending")
        await client.post(f"/api/v1/reviews/{review.id}/approve", headers=AUTH)
        university_update_stats.assert_called_once()
        kwargs = university_update_stats.call_args.kwargs
        assert kwargs["action"] == "approve"
        assert kwargs["rating"] == review.rating

    @pytest.mark.asyncio
    async def test_approve_creates_moderation_log(
        self, client, db_session, mock_as_admin, university_update_stats
    ):
        # также создаются логи
        from sqlalchemy import select
        from app.models import ModerationLog

        review = await make_review(db_session, status="pending")
        await client.post(f"/api/v1/reviews/{review.id}/approve", headers=AUTH)

        result = await db_session.execute(
            select(ModerationLog).where(ModerationLog.review_id == review.id)
        )
        log = result.scalar_one_or_none()
        assert log is not None
        assert log.action == "approve"
        assert log.moderator_id == ADMIN_USER["user_id"]

    @pytest.mark.asyncio
    async def test_approve_already_approved(
        self, client, db_session, mock_as_admin, university_update_stats
    ):
    #   если уже одобряли этот отзыв - 400
        review = await make_review(db_session, status="approved")
        resp = await client.post(f"/api/v1/reviews/{review.id}/approve", headers=AUTH)
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_approve_nonexistent(self, client, mock_as_admin):
        # отзыв не найден - 404
        resp = await client.post("/api/v1/reviews/99999/approve", headers=AUTH)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_regular_user_cannot_approve(self, client, db_session, mock_as_regular_user):
        # обычный юзер не сможет одобрить, возвращаем 403
        review = await make_review(db_session, status="pending")
        resp = await client.post(f"/api/v1/reviews/{review.id}/approve", headers=AUTH)
        assert resp.status_code == 403


# POST /api/v1/reviews/{id}/reject
class TestRejectReview:

    @pytest.mark.asyncio
    async def test_admin_rejects_pending(self, client, db_session, mock_as_admin):
        # отклонили пендинг значит статус новый - реджект (плюс причина какая то есть)
        review = await make_review(db_session, status="pending")
        resp = await client.post(
            f"/api/v1/reviews/{review.id}/reject",
            json={"reason": "Нарушение правил сервиса"},
            headers=AUTH,
        )
        assert resp.status_code == 200
        assert resp.json()["status"] == "rejected"

    @pytest.mark.asyncio
    async def test_reject_creates_log_with_reason(self, client, db_session, mock_as_admin):
    #    в логи модерации падает та причина как раз
        from sqlalchemy import select
        from app.models import ModerationLog

        review = await make_review(db_session, status="pending")
        reason_text = "Содержит оскорбления"
        await client.post(
            f"/api/v1/reviews/{review.id}/reject",
            json={"reason": reason_text},
            headers=AUTH,
        )

        result = await db_session.execute(
            select(ModerationLog).where(ModerationLog.review_id == review.id)
        )
        log = result.scalar_one_or_none()
        assert log is not None
        assert log.action == "reject"
        assert log.reason == reason_text
        assert log.moderator_id == ADMIN_USER["user_id"]

    @pytest.mark.asyncio
    async def test_reject_without_reason_fails(self, client, db_session, mock_as_admin):
        # отклонение без причины (422 - то есть по сути ошибка валдиации)
        review = await make_review(db_session, status="pending")
        resp = await client.post(
            f"/api/v1/reviews/{review.id}/reject",
            json={"reason": "ок"},  # меньше 5 символов
            headers=AUTH,
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_reject_already_rejected(self, client, db_session, mock_as_admin):
        # повторное отклонение 
        review = await make_review(db_session, status="rejected")
        resp = await client.post(
            f"/api/v1/reviews/{review.id}/reject",
            json={"reason": "Повторная проверка"},
            headers=AUTH,
        )
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_reject_does_not_call_university_stats(
        self, client, db_session, mock_as_admin, university_update_stats
    ):
        # отклоненый отзыв не обновляет стату вуза
        review = await make_review(db_session, status="pending")
        await client.post(
            f"/api/v1/reviews/{review.id}/reject",
            json={"reason": "Нарушение правил"},
            headers=AUTH,
        )
        university_update_stats.assert_not_called()

    @pytest.mark.asyncio
    async def test_regular_user_cannot_reject(self, client, db_session, mock_as_regular_user):
        # юзер не отклоняет 
        review = await make_review(db_session, status="pending")
        resp = await client.post(
            f"/api/v1/reviews/{review.id}/reject",
            json={"reason": "Нарушение правил"},
            headers=AUTH,
        )
        assert resp.status_code == 403
