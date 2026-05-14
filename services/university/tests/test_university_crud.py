"""
 unit-тесты логики в university_crud.py
"""
import pytest
from conftest import make_university

from app.api.crud.university_crud import (
    create_university,
    get_all_universities,
    get_university_by_id,
    update_university_statistics,
)
from app.api.schemas.university_schema import UniversityBase
from app.errors.exceptions import UniversityAlreadyExistsException

# создание уника
class TestCreateUniversity:

    @pytest.mark.asyncio
    async def test_create_success(self, db_session):
        data = UniversityBase(
            name="МФТИ",
            city="Долгопрудный",
            description="Физтех",
            has_dormitory=True,
            website="https://mipt.ru",
        )
        uni = await create_university(db_session, data)
        assert uni.id is not None
        assert uni.name == "МФТИ"
        assert uni.city == "Долгопрудный"
        assert uni.rating == 0.0
        assert uni.reviews_count == 0

    @pytest.mark.asyncio
    async def test_create_duplicate_raises(self, db_session):
        # создание с повторением названия
        data = UniversityBase(
            name="НГУ", city="Новосибирск", has_dormitory=True
        )
        await create_university(db_session, data)

        with pytest.raises(UniversityAlreadyExistsException):
            await create_university(db_session, data)

    @pytest.mark.asyncio
    async def test_create_sets_default_rating(self, db_session):
        # у нового нулевой рейтинг
        data = UniversityBase(name="Тестовый вуз", city="Тест", has_dormitory=False)
        uni = await create_university(db_session, data)
        assert uni.rating == 0.0
        assert uni.reviews_count == 0


# get_all_universities
class TestGetAllUniversities:

    @pytest.mark.asyncio
    async def test_returns_all(self, db_session):
        await make_university(db_session, name="МГУ",  city="Москва")
        await make_university(db_session, name="СПбГУ", city="Санкт-Петербург")

        result = await get_all_universities(db_session)
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_filter_by_min_rating(self, db_session):
        await make_university(db_session, name="А", city="X", rating=4.5)
        await make_university(db_session, name="Б", city="X", rating=3.0)
        await make_university(db_session, name="В", city="X", rating=2.0)

        result = await get_all_universities(db_session, min_rating=4.0)
        assert len(result) == 1
        assert result[0].name == "А"

    @pytest.mark.asyncio
    async def test_filter_by_dormitory(self, db_session):
        await make_university(db_session, name="С общежитием",    city="X", has_dormitory=True)
        await make_university(db_session, name="Без общежития",   city="X", has_dormitory=False)

        result = await get_all_universities(db_session, has_dormitory=True)
        assert len(result) == 1
        assert result[0].has_dormitory is True

    @pytest.mark.asyncio
    async def test_combined_filters(self, db_session):
        # несколько филтьров
        await make_university(db_session, name="А", city="Москва", rating=4.0, has_dormitory=True)
        await make_university(db_session, name="Б", city="Москва", rating=2.0, has_dormitory=True)
        await make_university(db_session, name="В", city="Казань",  rating=4.5, has_dormitory=True)

        result = await get_all_universities(db_session, city="Москва", min_rating=3.5)
        assert len(result) == 1
        assert result[0].name == "А"

    @pytest.mark.asyncio
    async def test_empty_db_returns_empty_list(self, db_session):
        result = await get_all_universities(db_session)
        assert result == []


# get_university_by_id
class TestGetUniversityById:

    @pytest.mark.asyncio
    async def test_found(self, db_session):
        uni = await make_university(db_session, name="ИТМО")
        result = await get_university_by_id(db_session, uni.id)
        assert result is not None
        assert result.name == "ИТМО"

    @pytest.mark.asyncio
    async def test_not_found_returns_none(self, db_session):
        result = await get_university_by_id(db_session, 99999)
        assert result is None


# update_university_statistics
class TestUpdateUniversityStatistics:

    @pytest.mark.asyncio
    async def test_first_approve_sets_rating(self, db_session):
        # первый отзыв = вся оценка
        uni = await make_university(db_session, name="Х", city="Х", rating=0.0, reviews_count=0)
        updated = await update_university_statistics(db_session, uni.id, new_score=4.0, action="approve")
        assert updated.reviews_count == 1
        assert updated.rating == 4.0

    @pytest.mark.asyncio
    async def test_second_approve_averages_rating(self, db_session):
        # второй отзыв - ср.арифмет.
        uni = await make_university(db_session, name="Х", city="Х", rating=4.0, reviews_count=1)
        updated = await update_university_statistics(db_session, uni.id, new_score=2.0, action="approve")
        assert updated.reviews_count == 2
        assert updated.rating == 3.0 

    @pytest.mark.asyncio
    async def test_delete_recalculates_rating(self, db_session):
        # Было 2 отзыва: рейтинг 4.0 (суммарно 8.0). Удаляем отзыв с оценкой 2.0: (8-2)/1 = 6
        # но так как 6 больше 5 то ставим пять просто
        uni = await make_university(db_session, name="Х", city="Х", rating=4.0, reviews_count=2)
        updated = await update_university_statistics(db_session, uni.id, new_score=2.0, action="delete")
        assert updated.reviews_count == 1
        assert updated.rating == 5.0

    @pytest.mark.asyncio
    async def test_delete_last_review_resets_to_zero(self, db_session):
        # удаляем последний отзыв - всё по нулям
        uni = await make_university(db_session, name="Х", city="Х", rating=3.5, reviews_count=1)
        updated = await update_university_statistics(db_session, uni.id, new_score=3.5, action="delete")
        assert updated.reviews_count == 0
        assert updated.rating == 0.0

    @pytest.mark.asyncio
    async def test_rating_clamped_to_5(self, db_session):
        uni = await make_university(db_session, name="Х", city="Х", rating=5.0, reviews_count=10)
        updated = await update_university_statistics(db_session, uni.id, new_score=5.0, action="approve")
        assert updated.rating <= 5.0

    @pytest.mark.asyncio
    async def test_rating_clamped_to_1_minimum(self, db_session):
        uni = await make_university(db_session, name="Х", city="Х", rating=1.0, reviews_count=1)
        updated = await update_university_statistics(db_session, uni.id, new_score=1.0, action="approve")
        assert updated.rating >= 1.0

    @pytest.mark.asyncio
    async def test_nonexistent_university_returns_none(self, db_session):
        result = await update_university_statistics(db_session, 99999, new_score=4.0)
        assert result is None