# seeds/run_seeder.py
import argparse
import asyncio
import sys
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent))

from app.database import AsyncSessionLocal, engine
from seeds.seeder_review import ReviewSeeder


async def run_seeder(count: int = 5):
    seeder = ReviewSeeder(engine, AsyncSessionLocal)

    await seeder.seed(count=count)
    print("Готово!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seeder для отзывов")
    parser.add_argument("--count", type=int, default=5, help="Количество отзывов")
    parser.add_argument("--type", choices=["basic", "advanced"], default="basic", help="Тип seeder'а")

    args = parser.parse_args()

    asyncio.run(run_seeder(args.count))
