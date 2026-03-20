from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_async_session
from api.schemas.university_schema import (
    UniversityRead, 
    UniversityCreate, 
    UniversityRatingUpdate
)
import api.crud.university_crud as university_crud
from errors.exceptions import UniversityNotFoundException
from logger.logger import logger

router = APIRouter(tags=["Universities"])

@router.get(
    "/universities/", 
    response_model=list[UniversityRead],
    status_code=status.HTTP_200_OK,
    summary="Получить список всех ВУЗов с фильтрацией"
)
async def get_universities(
    city: str | None = None,
    min_rating: float | None = None,
    has_dormitory: bool | None = None,
    session: AsyncSession = Depends(get_async_session)
):
    logger.info(f"Запрос на список ВУЗов: city={city}, min_rating={min_rating}, dorm={has_dormitory}")
    return await university_crud.get_all_universities(
        session, 
        city=city, 
        min_rating=min_rating, 
        has_dormitory=has_dormitory
    )

@router.get(
    "/universities/{uni_id}", 
    response_model=UniversityRead,
    status_code=status.HTTP_200_OK,
    summary="Получить ВУЗ по ID"
)
async def get_university(uni_id: int, session: AsyncSession = Depends(get_async_session)):
    logger.info(f"Запрос данных ВУЗа с ID: {uni_id}")
    db_university = await university_crud.get_university_by_id(session, uni_id)
    
    if db_university is None:
        logger.warning(f"ВУЗ с ID {uni_id} не найден")
        raise UniversityNotFoundException()
        
    logger.debug(f"Данные извлечены для: {db_university.name}")
    return db_university

@router.post(
    "/universities/", 
    response_model=UniversityRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить новый ВУЗ"
)
async def add_university(
    uni: UniversityCreate, 
    session: AsyncSession = Depends(get_async_session)
):
    logger.info(f"Запрос на создание ВУЗа: {uni.name}")
    return await university_crud.create_university(session, uni)

@router.patch(
    "/universities/{uni_id}/update-rating",
    response_model=UniversityRead,
    summary="Обновить статистику рейтинга (внутренний эндпоинт)"
)
async def update_rating(
    uni_id: int, 
    update_data: UniversityRatingUpdate, 
    session: AsyncSession = Depends(get_async_session)
):
    logger.info(f"Обновление рейтинга ВУЗа {uni_id}. Новая оценка: {update_data.new_score}")
    
    db_university = await university_crud.update_university_statistics(
        session, uni_id, update_data.new_score
    )

    if db_university is None:
        logger.warning(f"ВУЗ {uni_id} не найден для обновления рейтинга")
        raise UniversityNotFoundException()
        
    return db_university