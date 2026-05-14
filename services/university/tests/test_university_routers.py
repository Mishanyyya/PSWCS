
# тесты HTTP-эндпоинтов University service

import pytest
from conftest import make_university



# GET /universities/
class TestGetUniversities:

    @pytest.mark.asyncio
    async def test_empty_list(self, client):
        resp = await client.get("/universities/")
        assert resp.status_code == 200
        assert resp.json() == []

    @pytest.mark.asyncio
    async def test_returns_all(self, client, db_session):
        await make_university(db_session, name="МГУ",   city="Москва")
        await make_university(db_session, name="СПбГУ", city="Санкт-Петербург")
        resp = await client.get("/universities/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2



# GET /universities/{id}

class TestGetUniversityById:

    @pytest.mark.asyncio
    async def test_found(self, client, db_session):
        uni = await make_university(db_session, name="ИТМО", city="Санкт-Петербург")
        resp = await client.get(f"/universities/{uni.id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "ИТМО"

    @pytest.mark.asyncio
    async def test_not_found(self, client):
        resp = await client.get("/universities/99999")
        assert resp.status_code == 404

# POST /universities/

class TestCreateUniversity:

    PAYLOAD = {
        "name": "Новый вуз",
        "city": "Казань",
        "description": "Описание вуза",
        "has_dormitory": True,
        "website": "https://newuni.ru",
    }

    @pytest.mark.asyncio
    async def test_create_success(self, client):
        resp = await client.post("/universities/", json=self.PAYLOAD)
        assert resp.status_code == 201
        data = resp.json()
        assert data["name"] == "Новый вуз"
        assert data["rating"] == 0.0
        assert data["reviews_count"] == 0

    @pytest.mark.asyncio
    async def test_create_duplicate(self, client):
        await client.post("/universities/", json=self.PAYLOAD)
        resp = await client.post("/universities/", json=self.PAYLOAD)
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_create_name_too_short(self, client):
        resp = await client.post("/universities/", json={**self.PAYLOAD, "name": "А"})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_create_missing_required_fields(self, client):
        resp = await client.post("/universities/", json={"name": "Только имя"})
        assert resp.status_code == 422


class TestUpdateRating:

    @pytest.mark.asyncio
    async def test_not_found(self, client):
        resp = await client.patch(
            "/universities/99999/update-rating",
            json={"new_score": 4.0, "action": "approve"},
        )
        assert resp.status_code == 404