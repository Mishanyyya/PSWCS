import api.crud.university_crud as university_crud
from api.dependencies.auth import get_current_user, role_required
from api.schemas.university_schema import UniversityCreate, UniversityRatingUpdate, UniversityRead
from db.database import get_async_session
from errors.exceptions import UniversityNotFoundException
from fastapi import APIRouter, Depends, status
from logger.logger import logger
from sqlalchemy.ext.asyncio import AsyncSession


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
    session: AsyncSession = Depends(get_async_session),
    user: dict = Depends(get_current_user)
):
    logger.info(f"Запрос на список ВУЗов от пользователя {user['email']}: city={city}, min_rating={min_rating}, dorm={has_dormitory}")
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
async def get_university(
    uni_id: int,
    session: AsyncSession = Depends(get_async_session),
    user: dict = Depends(get_current_user)
):
    logger.info(f"Запрос данных ВУЗа от пользователя {user['email']} с ID: {uni_id}")
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
    summary="Добавить новый ВУЗ",
)
async def add_university(
    uni: UniversityCreate,
    session: AsyncSession = Depends(get_async_session),
    admin_user: dict = Depends(role_required(["admin"]))
):
    logger.info(f"Админ {admin_user['email']} создает ВУЗ: {uni.name}")
    return await university_crud.create_university(session, uni)

@router.patch(
    "/universities/{uni_id}/update-rating",
    response_model=UniversityRead,
    status_code=status.HTTP_200_OK,
    summary="Обновить статистику рейтинга (внутренний эндпоинт)"
)
@router.patch(
    "/universities/{uni_id}/update-rating",
    response_model=UniversityRead,
    status_code=status.HTTP_200_OK,
    summary="Обновить статистику рейтинга (approve/delete)"
)
async def update_rating(
    uni_id: int,
    update_data: UniversityRatingUpdate,
    session: AsyncSession = Depends(get_async_session),
    admin_user: dict = Depends(role_required(["admin"]))
):
    logger.info(f"Админ {admin_user['email']} запрашивает {update_data.action} для ВУЗа {uni_id}. Оценка: {update_data.new_score}")

    db_university = await university_crud.update_university_statistics(
        session,
        uni_id,
        update_data.new_score,
        update_data.action
    )

    if db_university is None:
        raise UniversityNotFoundException()

    return db_university

@router.delete(
    "/universities/{uni_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить ВУЗ"
)
async def delete_university(
    uni_id: int,
    session: AsyncSession = Depends(get_async_session),
    admin_user: dict = Depends(role_required(["admin"]))
):
    logger.info(f"Админ {admin_user['email']} инициировал удаление ВУЗа ID: {uni_id}")

    success = await university_crud.delete_university(session, uni_id)

    if not success:
        raise UniversityNotFoundException()

    return None
