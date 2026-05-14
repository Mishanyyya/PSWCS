from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.university_model import University
from app.api.schemas.university_schema import UniversityBase
from app.errors.exceptions import UniversityAlreadyExistsException
from app.logger.logger import logger

async def create_university(session: AsyncSession, uni_data: UniversityBase):
    query = select(University).where(University.name == uni_data.name)
    result = await session.execute(query)
    existing_uni = result.scalar_one_or_none()
    if existing_uni:
        logger.error(f"Попытка добавления существующего ВУЗа: {uni_data.name}")
        raise UniversityAlreadyExistsException()
    
    new_uni = University(**uni_data.model_dump())
    session.add(new_uni)
    await session.commit()
    await session.refresh(new_uni)
    logger.info(f"Новый ВУЗ успешно добавлен: {uni_data.name}")
    return new_uni

async def get_all_universities(
    session: AsyncSession, 
    city: str | None = None, 
    min_rating: float | None = None, 
    has_dormitory: bool | None = None
):
    query = select(University)
    
    filters = []
    if city:
        filters.append(University.city.ilike(f"%{city}%"))
    if min_rating is not None:
        filters.append(University.rating >= min_rating)
    if has_dormitory is not None:
        filters.append(University.has_dormitory == has_dormitory)
    
    if filters:
        query = query.where(*filters)
        
    result = await session.execute(query)
    return result.scalars().all()

async def get_university_by_id(session: AsyncSession, uni_id: int):
    result = await session.execute(
        select(University).where(University.id == uni_id)
    )
    return result.scalar_one_or_none()

async def update_university_statistics(
    session: AsyncSession, 
    uni_id: int, 
    new_score: float,
    action: str = "approve"
):
    query = select(University).where(University.id == uni_id)
    result = await session.execute(query)
    university = result.scalar_one_or_none()
    
    if not university:
        return None

    if action == "approve":
        # Добавляем новый отзыв
        current_total_score = university.rating * university.reviews_count
        new_reviews_count = university.reviews_count + 1
        new_average_rating = (current_total_score + new_score) / new_reviews_count
        
    elif action == "delete":
        # Удаляем существующий отзыв
        if university.reviews_count <= 1:
            new_reviews_count = 0
            new_average_rating = 0
        else:
            current_total_score = university.rating * university.reviews_count
            new_reviews_count = university.reviews_count - 1
            new_average_rating = (current_total_score - new_score) / new_reviews_count
        
    
    else:
        # По умолчанию - approve
        current_total_score = university.rating * university.reviews_count
        new_reviews_count = university.reviews_count + 1
        new_average_rating = (current_total_score + new_score) / new_reviews_count

    if new_reviews_count == 0:
        final_rating = 0  # Нет отзывов - рейтинг 0
    else: final_rating = max(1.0, min(5.0, new_average_rating))

    university.rating = round(final_rating, 2)
    university.reviews_count = new_reviews_count
    
    await session.commit()
    await session.refresh(university)
    
    logger.info(f"Обновлена статистика для ВУЗа {uni_id}: action={action}, "
                f"рейтинг {university.rating}, отзывов {university.reviews_count}")
    return university