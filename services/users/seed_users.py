import argparse
import os
import random
from pathlib import Path
from typing import List, Dict, Any

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from faker import Faker

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Инициализация Faker
fake = Faker()

DEFAULT_ROLES_CONFIG = "admin:0.1,user:0.9"
DEFAULT_ADMIN_EMAIL = "admin@local.test"
DEFAULT_ADMIN_PASSWORD = "ChangeMe123!"
DEFAULT_ADMIN_FULL_NAME = "System Admin"
DEFAULT_CREDENTIALS_FILE = "users_credentials.txt"


def parse_roles_config(roles_config: str) -> List[Dict[str, Any]]:
    roles: List[Dict[str, Any]] = []
    for item in roles_config.split(","):
        raw = item.strip()
        if not raw:
            continue
        name, weight = raw.split(":", maxsplit=1)
        roles.append({"name": name.strip(), "weight": float(weight.strip())})

    if not roles:
        raise ValueError("SEED_USER_ROLES должен содержать хотя бы одну роль")

    return roles


def get_seed_config() -> Dict[str, Any]:
    roles_config = os.getenv("SEED_USER_ROLES", DEFAULT_ROLES_CONFIG)
    return {
        "admin_email": os.getenv("SEED_ADMIN_EMAIL", DEFAULT_ADMIN_EMAIL),
        "admin_password": os.getenv("SEED_ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD),
        "admin_full_name": os.getenv("SEED_ADMIN_FULL_NAME", DEFAULT_ADMIN_FULL_NAME),
        "credentials_file": os.getenv("SEED_OUTPUT_FILE", DEFAULT_CREDENTIALS_FILE),
        "roles": parse_roles_config(roles_config),
    }


def get_random_role(roles_config: List[Dict[str, Any]]) -> str:
    roles = [r["name"] for r in roles_config]
    weights = [r["weight"] for r in roles_config]
    return random.choices(roles, weights=weights)[0]


def generate_users(count: int, seed_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    users = []
    emails = set()

    for i in range(count):
        while True:
            if i == 0 and count > 0:
                email = seed_config["admin_email"]
                role = "admin"
                full_name = seed_config["admin_full_name"]
                password = seed_config["admin_password"]
            else:
                email = fake.unique.email()
                role = get_random_role(seed_config["roles"])
                full_name = fake.name()
                password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)

            if email not in emails:
                emails.add(email)
                break

        users.append({
            "role": role,
            "email": email,
            "password": password,
            "full_name": full_name,
        })

    return users


def seed_sync(database_url: str, count: int = 10, force: bool = False, credentials_file: str = DEFAULT_CREDENTIALS_FILE):
    if "+asyncpg" in database_url:
        database_url = database_url.replace("+asyncpg", "")
        print(f"URL содержал asyncpg, заменен на: {database_url}")

    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        result = session.execute(text("SELECT COUNT(*) FROM users"))
        existing_count = result.scalar()

        if existing_count > 0 and not force:
            print(f"В таблице users уже есть {existing_count} записей.")
            response = input("Хотите удалить существующих пользователей и добавить новых? (y/N): ")
            if response.lower() != 'y':
                print("Операция отменена.")
                return
            session.execute(text("DELETE FROM users"))
            session.commit()
            print("Существующие пользователи удалены.")
        elif existing_count > 0 and force:
            session.execute(text("DELETE FROM users"))
            session.commit()
            print("Существующие пользователи удалены (force mode).")

        print(f"Генерация {count} пользователей...")
        seed_config = get_seed_config()
        users = generate_users(count, seed_config)

        for user in users:
            hashed_password = pwd_context.hash(user["password"])
            session.execute(
                text("""
                    INSERT INTO users (role, email, hashed_password, full_name)
                    VALUES (:role, :email, :hashed_password, :full_name)
                """),
                {
                    "role": user["role"],
                    "email": user["email"],
                    "hashed_password": hashed_password,
                    "full_name": user["full_name"],
                },
            )

        session.commit()

        print(f"\nУспешно добавлено {len(users)} пользователей.")
        print("\nСтатистика по ролям:")

        role_stats = {}
        for user in users:
            role_stats[user["role"]] = role_stats.get(user["role"], 0) + 1

        for role, count_role in role_stats.items():
            print(f"  {role}: {count_role} ({count_role/len(users)*100:.1f}%)")

        print("\nПримеры созданных пользователей (первые 5):")
        for i, user in enumerate(users[:5]):
            print(f"  {i+1}. Email: {user['email']}, Role: {user['role']}, Password: {user['password']}")

        if len(users) > 5:
            print(f"  ... и еще {len(users)-5} пользователей")

        save_credentials_to_file(users, credentials_file)

    except Exception as e:
        session.rollback()
        print(f"Ошибка при сидинге: {e}")
        raise
    finally:
        session.close()


def save_credentials_to_file(users: List[Dict[str, Any]], filename: str = DEFAULT_CREDENTIALS_FILE):
    output_path = Path(filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("СОЗДАННЫЕ ПОЛЬЗОВАТЕЛИ\n")
        f.write("=" * 60 + "\n\n")

        for i, user in enumerate(users, 1):
            f.write(f"{i}. Email: {user['email']}\n")
            f.write(f"   Password: {user['password']}\n")
            f.write(f"   Role: {user['role']}\n")
            f.write(f"   Full Name: {user['full_name']}\n")
            f.write("-" * 40 + "\n")

        f.write(f"\nВсего создано: {len(users)} пользователей\n")

    print(f"\nДанные для входа сохранены в файл: {output_path}")


def resolve_database_url(cli_database_url: str | None) -> str:
    if cli_database_url:
        return cli_database_url

    env_database_url = os.getenv("DATABASE_URL")
    if env_database_url:
        return env_database_url

    raise RuntimeError(
        "DATABASE_URL не задан. Передайте --db-url или установите переменную окружения DATABASE_URL"
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Генерация тестовых пользователей")
    parser.add_argument(
        "count",
        type=int,
        nargs="?",
        default=10,
        help="Количество пользователей для генерации (по умолчанию: 10)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Принудительно удалить существующих пользователей без подтверждения",
    )
    parser.add_argument(
        "--db-url",
        type=str,
        help="URL базы данных (если не указан, используется DATABASE_URL из env)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=os.getenv("SEED_OUTPUT_FILE", DEFAULT_CREDENTIALS_FILE),
        help="Файл для сохранения сгенерированных логинов/паролей",
    )

    args = parser.parse_args()

    database_url = resolve_database_url(args.db_url)

    print(f"Запуск seeder для базы данных: {database_url}")
    print(f"Будет сгенерировано {args.count} пользователей")

    seed_sync(database_url, args.count, args.force, args.output)