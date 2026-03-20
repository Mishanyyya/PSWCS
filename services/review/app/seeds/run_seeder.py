# seeds/run_seeder.py
import asyncio
import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from seeds.seeder_review import ReviewSeeder
from app.database import engine, AsyncSessionLocal

async def run_seeder(seed_type: str = "basic", count: int = 50):
    """Запуск seeder'а с параметрами"""
    
    print(f"Запуск {seed_type} seeder'а с {count} отзывами...")
    
    if seed_type == "basic":
        seeder = ReviewSeeder(engine, AsyncSessionLocal)
    else:
        print(f"Неизвестный тип: {seed_type}")
        return
    
    await seeder.seed(count=count)
    print("Готово!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seeder для отзывов")
    parser.add_argument("--count", type=int, default=10, help="Количество отзывов")
    parser.add_argument("--type", choices=["basic", "advanced"], default="basic", 
                       help="Тип seeder'а")
    
    args = parser.parse_args()
    
    asyncio.run(run_seeder(args.type, args.count))