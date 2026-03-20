# app/seeds/seeder_review.py
import asyncio
import uuid
import random
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

import sys
from pathlib import Path

# Добавляем путь к корневой папке проекта
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.database import Base
from app.models import Review, ModerationLog

# Настройки - берем из database.py или прописываем здесь
DATABASE_URL = "postgresql+asyncpg://postgres:pass@localhost:5432/review_db"

# Возможные статусы
STATUSES = ["pending", "approved", "rejected"]

# Возможные действия модерации
MODERATION_ACTIONS = ["approve", "reject", "flag"]

class ReviewSeeder:
    def __init__(self, engine, session_maker):
        self.engine = engine
        self.session_maker = session_maker
        self.fake = Faker("ru_RU")
        self.university_ids = [
            uuid.UUID('11111111-1111-1111-1111-111111111111'),
            uuid.UUID('22222222-2222-2222-2222-222222222222'),
            uuid.UUID('33333333-3333-3333-3333-333333333333'),
            uuid.UUID('44444444-4444-4444-4444-444444444444'),
            uuid.UUID('55555555-5555-5555-5555-555555555555'),
        ]
        
        # Генерируем больше авторов
        self.author_ids = [
            uuid.UUID('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'),
            uuid.UUID('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'),
            uuid.UUID('cccccccc-cccc-cccc-cccc-cccccccccccc'),
            uuid.UUID('dddddddd-dddd-dddd-dddd-dddddddddddd'),
            uuid.UUID('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee'),
            uuid.UUID('ffffffff-ffff-ffff-ffff-ffffffffffff'),
            uuid.UUID('11111111-1111-1111-1111-111111111112'),
            uuid.UUID('22222222-2222-2222-2222-222222222223'),
            uuid.UUID('33333333-3333-3333-3333-333333333334'),
            uuid.UUID('44444444-4444-4444-4444-444444444445'),
        ]
        
        # Для отслеживания использованных комбинаций
        self.used_combinations = set()
    
    def get_unique_combination(self):
        """Генерирует уникальную комбинацию university_id и author_id"""
        max_attempts = 100
        for _ in range(max_attempts):
            uni_id = random.choice(self.university_ids)
            author_id = random.choice(self.author_ids)
            combination = (uni_id, author_id)
            
            if combination not in self.used_combinations:
                self.used_combinations.add(combination)
                return uni_id, author_id
        
        # Если все комбинации использованы, расширяем списки
        self.expand_ids()
        return self.get_unique_combination()
    
    def expand_ids(self):
        """Расширяет списки ID если все комбинации использованы"""
        new_uni_id = uuid.uuid4()
        new_author_id = uuid.uuid4()
        self.university_ids.append(new_uni_id)
        self.author_ids.append(new_author_id)
        print(f"Добавлены новые ID: {new_uni_id}, {new_author_id}")
    
    def generate_review(self, index: int = None) -> Review:
        """Генерация одного случайного отзыва"""
        
        # Получаем уникальную комбинацию
        university_id, author_id = self.get_unique_combination()
        
        # Случайные даты за последние 6 месяцев
        created_at = self.fake.date_time_between(start_date='-180d', end_date='now')
        updated_at = created_at + timedelta(days=random.randint(0, 30))
        
        # Генерация рейтинга (1-5) с разными весами
        rating = random.choices([1, 2, 3, 4, 5], weights=[0.1, 0.15, 0.25, 0.3, 0.2])[0]
        
        # Генерация заголовка в зависимости от рейтинга
        if rating >= 4:
            title_prefix = ["Отлично!", "Супер!", "Рекомендую!", "Замечательно!", "Прекрасно!"]
            title = f"{random.choice(title_prefix)} {self.fake.catch_phrase()}"
        elif rating <= 2:
            title_prefix = ["Ужасно!", "Разочарован!", "Не рекомендую!", "Плохо!", "Ожидал большего!"]
            title = f"{random.choice(title_prefix)} {self.fake.catch_phrase()}"
        else:
            title = self.fake.sentence(nb_words=5)
        
        if rating >= 4:
            body = f"{self.fake.paragraph(nb_sentences=3)} {' '.join(self.fake.words(nb=5))} {self.fake.paragraph(nb_sentences=2)}"
        elif rating <= 2:
            body = f"{self.fake.paragraph(nb_sentences=4)} {' '.join(self.fake.words(nb=3))} {self.fake.paragraph(nb_sentences=2)}"
        else:
            body = self.fake.paragraph(nb_sentences=5)
        
        # Статус (с большей вероятностью approved)
        status = random.choices(STATUSES, weights=[0.2, 0.7, 0.1])[0]
        
        return Review(
            id=uuid.uuid4(),
            university_id=university_id,
            author_id=author_id,
            rating=rating,
            title=title[:255],  # Ограничение длины
            body=body,
            status=status,
            is_anonymous=random.choice([True, False]),
            created_at=created_at,
            updated_at=updated_at
        )
    
    def generate_moderation_log(self, review_id: uuid.UUID, created_at: datetime, status: str) -> ModerationLog | None:
        """Генерация лога модерации для одобренных/отклоненных отзывов"""
        
        # Генерируем лог только для approved или rejected
        if status == "pending":
            return None
        
        # Генерируем лог с вероятностью 0.7
        if random.random() > 0.7:
            return None
        
        action = "approve" if status == "approved" else "reject"
        
        # Причины для отклонения
        rejection_reasons = [
            "Содержит нецензурную лексику",
            "Оскорбления в адрес университета",
            "Не соответствует тематике",
            "Дубликат отзыва",
            "Нарушение правил публикации",
            "Спам",
            "Рекламный характер"
        ]
        
        reason = None
        if action == "reject":
            reason = random.choice(rejection_reasons)
        
        # Дата лога обычно позже даты создания отзыва
        log_created_at = created_at + timedelta(hours=random.randint(1, 72))
        
        return ModerationLog(
            id=uuid.uuid4(),
            review_id=review_id,
            moderator_id=random.choice(self.author_ids),  # Используем существующих пользователей как модераторов
            action=action,
            reason=reason,
            created_at=log_created_at
        )
    
    async def seed(self, count: int = 50):
        """Заполнение БД тестовыми данными"""
        
        # Сбрасываем использованные комбинации при каждом запуске
        self.used_combinations.clear()
        
        async with self.session_maker() as session:
            # Генерация отзывов
            reviews = []
            for i in range(count):
                try:
                    review = self.generate_review(i)
                    reviews.append(review)
                    
                    if (i + 1) % 10 == 0:
                        print(f"Сгенерировано {i + 1} отзывов...")
                except Exception as e:
                    print(f"Ошибка при генерации отзыва {i+1}: {e}")
                    continue
            
            # Добавляем отзывы в сессию
            session.add_all(reviews)
            await session.flush()  # Чтобы получить ID отзывов
            
            # Генерация логов модерации для некоторых отзывов
            logs = []
            for review in reviews:
                log = self.generate_moderation_log(review.id, review.created_at, review.status)
                if log:
                    logs.append(log)
            
            # Добавляем логи
            if logs:
                session.add_all(logs)
                print(f"Сгенерировано {len(logs)} логов модерации")
            
            # Коммитим изменения
            await session.commit()
            print(f"Успешно добавлено {len(reviews)} отзывов в БД")



# Если нужно запустить напрямую
async def main():
    engine = create_async_engine(DATABASE_URL, echo=True)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    
    try:
        # Создаем таблицы (если нужно)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Создаем и запускаем seeder
        seeder = ReviewSeeder(engine, session_maker)
        
        # Генерируем 50 отзывов
        await seeder.seed(count=50)
        
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())