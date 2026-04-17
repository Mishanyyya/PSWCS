import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.config import settings
from db.database import get_async_session, engine
from models.university_model import University
from api.schemas.university_schema import UniversityCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_seeder")

UNIVERSITIES_DATA = [
    {
        "name": "МИЭТ",
        "city": "Москва",
        "description": "Лучший технический вуз страны.",
        "has_dormitory": True,
        "website": "https://miet.ru",
        "rating": 0,
        "reviews_count": 0
    },
    {
        "name": "СПбГУ",
        "city": "Санкт-Петербург",
        "description": "Один из старейших университетов России.",
        "has_dormitory": True,
        "website": "https://spbu.ru",
        "rating": 0,
        "reviews_count": 0
    },
    {
        "name": "УрФУ",
        "city": "Екатеринбург",
        "description": "Крупнейший федеральный университет.",
        "has_dormitory": True,
        "website": "https://urfu.ru",
        "rating": 0,
        "reviews_count": 0
    }
]

async def seed_data():
    logger.info("Начало процесса наполнения БД...")
    
    from sqlalchemy.orm import sessionmaker
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        for uni_data in UNIVERSITIES_DATA:
            query = select(University).where(University.name == uni_data["name"])
            result = await session.execute(query)
            if result.scalar_one_or_none():
                continue

            new_uni = University(**uni_data)
            session.add(new_uni)
            logger.info(f"Добавление ВУЗа: {uni_data['name']}")

        await session.commit()
    
    logger.info("Наполнение БД завершено успешно!")

if __name__ == "__main__":
    asyncio.run(seed_data())