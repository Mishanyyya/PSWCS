from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.university_model import University
from api.schemas.university_schema import UniversityBase
from errors.exceptions import UniversityAlreadyExistsException
from logger.logger import logger

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

async def get_all_universities(session: AsyncSession):
    result = await session.execute(select(University))
    return result.scalars().all()

async def get_university_by_id(session: AsyncSession, uni_id: int):
    result = await session.execute(
        select(University).where(University.id == uni_id)
    )
    return result.scalar_one_or_none()