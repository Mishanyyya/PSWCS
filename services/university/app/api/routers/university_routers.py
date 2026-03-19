from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_async_session
from api.schemas.university_schema import UniversityRead, UniversityBase
import api.crud.university_crud as university_crud
from errors.exceptions import UniversityNotFoundException
from logger.logger import logger

router = APIRouter(tags=["Universities"])

@router.get(
    "/universities/", 
    response_model=list[UniversityRead],
    status_code=status.HTTP_200_OK,
    summary="Получить список всех ВУЗов"
)
async def get_universities(session: AsyncSession = Depends(get_async_session)):
    logger.info(f"Получен запрос на получение списка ВУЗов")
    return await university_crud.get_all_universities(session)

@router.get(
    "/universities/{uni_id}", 
    response_model=UniversityRead,
    status_code=status.HTTP_200_OK,
    summary="Получить ВУЗ по ID"
)
async def get_university(uni_id: int, session: AsyncSession = Depends(get_async_session)):
    logger.info(f"Получен запрос на получение ВУЗа с ID: {uni_id}")
    db_university = await university_crud.get_university_by_id(session, uni_id)
    if db_university is None:
        logger.warning(f"ВУЗ с ID {uni_id} не найден в базе данных")
        raise UniversityNotFoundException()
    logger.debug(f"Данные для ID {uni_id} успешно извлечены: {db_university.name}")
    return db_university

@router.post(
    "/universities/", 
    response_model=UniversityRead,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить новый ВУЗ")
async def add_university(uni: UniversityBase, session: AsyncSession = Depends(get_async_session)):
    logger.info(f"Получен запрос на добавление нового ВУЗа: {uni.name}")
    return await university_crud.create_university(session, uni)
