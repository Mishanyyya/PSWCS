# app/seeds/seeder_review.py
import asyncio
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Добавляем путь к корневой папке проекта
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.models import ModerationLog, Review
from app.config import settings
DATABASE_URL = settings.DATABASE_URL
STATUSES = ["pending", "approved", "rejected"]
MODERATION_ACTIONS = ["approve", "reject", "flag"]


class ReviewSeeder:
    def __init__(self, engine, session_maker):
        self.engine = engine
        self.session_maker = session_maker
        self.fake = Faker("ru_RU")
        
        self.university_ids = list(range(1, 21)) 
        self.author_ids = list(range(1, 31))      

        self.used_combinations = set()

    def get_unique_combination(self):
        # Получает уникальную комбинацию university_id и author_id
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
        # Расширяет списки ID если все комбинации использованы
        new_uni_id = max(self.university_ids) + 1
        new_author_id = max(self.author_ids) + 1
        self.university_ids.append(new_uni_id)
        self.author_ids.append(new_author_id)
        print(f"Добавлены новые ID: {new_uni_id}, {new_author_id}")

    def generate_review(self, index: int = None) -> Review:
        # Получаем уникальную комбинацию
        university_id, author_id = self.get_unique_combination()

        # Случайные даты за последние 6 месяцев
        created_at = self.fake.date_time_between(start_date="-180d", end_date="now")
        updated_at = created_at + timedelta(days=random.randint(0, 30))

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

        status = random.choices(STATUSES, weights=[0.2, 0.7, 0.1])[0]

        return Review(
            university_id=university_id,
            author_id=author_id,
            rating=rating,
            title=title[:255],
            body=body,
            status=status,
            is_anonymous=random.choice([True, False]),
            created_at=created_at,
            updated_at=updated_at,
        )

    def generate_moderation_log(self, review_id: int, created_at: datetime, status: str) -> ModerationLog | None:        
        # Генерируем лог только для approved или rejected
        if status == "pending":
            return None

        # С вероятностью 0.7
        if random.random() > 0.7:
            return None

        action = "approve" if status == "approved" else "reject"
        rejection_reasons = [
            "Содержит нецензурную лексику",
            "Оскорбления в адрес университета",
            "Не соответствует тематике",
            "Дубликат отзыва",
            "Нарушение правил публикации",
            "Спам",
            "Рекламный характер",
        ]

        reason = None
        if action == "reject":
            reason = random.choice(rejection_reasons)

        # Дата лога позже даты создания отзыва
        log_created_at = created_at + timedelta(hours=random.randint(1, 72))

        return ModerationLog(
            # id генерируется автоматически
            review_id=review_id,
            moderator_id=random.choice(self.author_ids),  # Используем существующих пользователей как модераторов
            action=action,
            reason=reason,
            created_at=log_created_at,
        )

    async def seed(self, count: int = 5):
        async with self.session_maker() as session:
            # Загружаем существующие пары из БД
            result = await session.execute(select(Review.university_id, Review.author_id))
            existing_pairs = {(row[0], row[1]) for row in result.fetchall()}
            # Используем их для исключения дубликатов
            self.used_combinations = existing_pairs

            # Генерация новых отзывов
            reviews = []
            for i in range(count):
                review = self.generate_review(i)
                reviews.append(review)

            session.add_all(reviews)
            await session.commit()
            
            # После коммита у отзывов появятся id, теперь можно добавить логи
            for review in reviews:
                log = self.generate_moderation_log(review.id, review.created_at, review.status)
                if log:
                    session.add(log)
            
            await session.commit()
            print(f"Успешно добавлено {len(reviews)} отзывов")


async def main():
    engine = create_async_engine(DATABASE_URL, echo=True)
    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    try:
        seeder = ReviewSeeder(engine, session_maker)
        await seeder.seed(count=20) 

    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())