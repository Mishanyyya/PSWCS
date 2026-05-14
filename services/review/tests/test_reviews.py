"""
тесты для app/routers/reviews.py
"""
import pytest
from conftest import make_review, REGULAR_USER, OTHER_USER, AUTH



VALID_PAYLOAD = {
    "university_id": 1,
    "rating": 4,
    "title": "Хороший университет",
    "body": "Учился здесь четыре года и остался очень доволен качеством образования.",
    "is_anonymous": False,
}


class TestCreateReview:

    @pytest.mark.asyncio
    async def test_success(self, client, mock_as_regular_user, university_exists, university_update_stats):
        # успешное создание
        resp = await client.post("/api/v1/reviews/", json=VALID_PAYLOAD, headers=AUTH)
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending"
        assert data["author_id"] == REGULAR_USER["user_id"]
        assert data["rating"] == 4

    @pytest.mark.asyncio
    async def test_unauthorized(self, client, mock_as_unauth, university_exists):
    #    нет токена валидного 
        resp = await client.post("/api/v1/reviews/", json=VALID_PAYLOAD, headers=AUTH)
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_university_not_found(self, client, mock_as_regular_user, university_not_exists):
    #    нет вуза
        resp = await client.post("/api/v1/reviews/", json=VALID_PAYLOAD, headers=AUTH)
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_duplicate_review(
        self, client, db_session, mock_as_regular_user, university_exists, university_update_stats
    ):
        # повторно на тот же вуз
        await make_review(db_session, university_id=1, author_id=REGULAR_USER["user_id"])
        resp = await client.post("/api/v1/reviews/", json=VALID_PAYLOAD, headers=AUTH)
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_rating_too_high(self, client, mock_as_regular_user, university_exists):
    #    рейтинг больше 5 (у нас 1 <= рейтинг <= 5)
        resp = await client.post(
            "/api/v1/reviews/", json={**VALID_PAYLOAD, "rating": 6}, headers=AUTH
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_rating_too_low(self, client, mock_as_regular_user, university_exists):
        resp = await client.post(
            "/api/v1/reviews/", json={**VALID_PAYLOAD, "rating": 0}, headers=AUTH
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_body_too_short(self, client, mock_as_regular_user, university_exists):
        # короткий отзыв (допустим не считаем его достоверным , поэтому короткие не пройдут валидацию)
        resp = await client.post(
            "/api/v1/reviews/", json={**VALID_PAYLOAD, "body": "Коротко."}, headers=AUTH
        )
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_title_too_short(self, client, mock_as_regular_user, university_exists):
        # то же для заголовка
        resp = await client.post(
            "/api/v1/reviews/", json={**VALID_PAYLOAD, "title": "Hi"}, headers=AUTH
        )
        assert resp.status_code == 422

# GET /api/v1/reviews/my  — свои отзывы
class TestGetMyReviews:

    @pytest.mark.asyncio
    async def test_empty_list(self, client, mock_as_regular_user):
        # если нет отзывов - всё ок, просто пустой список
        resp = await client.get("/api/v1/reviews/my", headers=AUTH)
        assert resp.status_code == 200
        assert resp.json()["total"] == 0

    @pytest.mark.asyncio
    async def test_returns_only_own(self, client, db_session, mock_as_regular_user):
        # не возвращает чужие отзывы
        await make_review(db_session, author_id=REGULAR_USER["user_id"], university_id=1)
        await make_review(db_session, author_id=OTHER_USER["user_id"],   university_id=2)

        resp = await client.get("/api/v1/reviews/my", headers=AUTH)
        data = resp.json()
        assert data["total"] == 1
        assert data["data"][0]["author_id"] == REGULAR_USER["user_id"]

    @pytest.mark.asyncio
    async def test_filter_by_status(self, client, db_session, mock_as_regular_user):
        # работоспособность фильтра по статусу
        uid = REGULAR_USER["user_id"]
        await make_review(db_session, author_id=uid, university_id=1, status="approved")
        await make_review(db_session, author_id=uid, university_id=2, status="pending")

        resp = await client.get("/api/v1/reviews/my?status=approved", headers=AUTH)
        data = resp.json()
        assert data["total"] == 1
        assert data["data"][0]["status"] == "approved"

    @pytest.mark.asyncio
    async def test_unauthorized(self, client, mock_as_unauth):
    #    ну и если нет токена
        resp = await client.get("/api/v1/reviews/my", headers=AUTH)
        assert resp.status_code == 401


# GET /api/v1/reviews/university/{id} 

class TestGetUniversityReviews:

    @pytest.mark.asyncio
    async def test_only_approved_by_default(self, client, db_session):
        # апрувд по умолчанию
        await make_review(db_session, university_id=10, author_id=1, status="approved")
        await make_review(db_session, university_id=10, author_id=2, status="pending")

        resp = await client.get("/api/v1/reviews/university/10")
        data = resp.json()
        assert data["total"] == 1
        assert data["data"][0]["status"] == "approved"


    @pytest.mark.asyncio
    async def test_sort_by_rating_desc(self, client, db_session):
        # сортировка по рейтингу от большего
        await make_review(db_session, university_id=30, author_id=1, rating=3, status="approved")
        await make_review(db_session, university_id=30, author_id=2, rating=5, status="approved")

        resp = await client.get("/api/v1/reviews/university/30?sort_by=rating&sort_order=desc")
        data = resp.json()["data"]
        assert data[0]["rating"] >= data[1]["rating"]

    @pytest.mark.asyncio
    async def test_no_reviews_returns_empty(self, client):
    #    ну опять же если пустой список то не выдаем ошибку
        resp = await client.get("/api/v1/reviews/university/9999")
        assert resp.status_code == 200
        assert resp.json()["total"] == 0



# DELETE /api/v1/reviews/{id}  
class TestDeleteReview:

    @pytest.mark.asyncio
    async def test_author_can_delete(
        self, client, db_session, mock_as_regular_user, university_update_stats
    ):
    # успешное удаление
        review = await make_review(db_session, author_id=REGULAR_USER["user_id"])
        resp = await client.delete(f"/api/v1/reviews/{review.id}", headers=AUTH)
        assert resp.status_code == 204


    @pytest.mark.asyncio
    async def test_admin_can_delete_any(
        self, client, db_session, mock_as_admin, university_update_stats
    ):
    #    админ удаляет чужой отзыв
        review = await make_review(db_session, author_id=REGULAR_USER["user_id"])
        resp = await client.delete(f"/api/v1/reviews/{review.id}", headers=AUTH)
        assert resp.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_approved_notifies_university(
        self, client, db_session, mock_as_regular_user, university_update_stats
    ):
        # при удалении отзыва уже одобренного - делаем пересчёт статы
        review = await make_review(
            db_session, author_id=REGULAR_USER["user_id"], status="approved"
        )
        await client.delete(f"/api/v1/reviews/{review.id}", headers=AUTH)
        university_update_stats.assert_called_once()
        assert university_update_stats.call_args.kwargs["action"] == "delete"

    @pytest.mark.asyncio
    async def test_delete_pending_no_stats_update(
        self, client, db_session, mock_as_regular_user, university_update_stats
    ):
        # если отзыв еще не одобрен, то НЕ вызваем обнову статы при удалении его
        review = await make_review(
            db_session, author_id=REGULAR_USER["user_id"], status="pending"
        )
        await client.delete(f"/api/v1/reviews/{review.id}", headers=AUTH)
        university_update_stats.assert_not_called()