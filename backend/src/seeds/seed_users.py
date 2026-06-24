import asyncio

from sqlalchemy import select

from src.core.database import async_session
from src.core.security import hash_password
from src.models.user import User, UserRole

# Набор пользователей по ролям
TEST_USERS = [
    {
        "email": "client@pizzatut.ru",
        "password": "test123",
        "name": "Клиент Тестов",
        "role": UserRole.CLIENT,
    },
    {
        "email": "manager@pizzatut.ru",
        "password": "test123",
        "name": "Менеджер Тестов",
        "role": UserRole.MANAGER,
    },
    {
        "email": "courier@pizzatut.ru",
        "password": "test123",
        "name": "Курьер Тестов",
        "role": UserRole.COURIER,
    },
    {
        "email": "admin@pizzatut.ru",
        "password": "test123",
        "name": "Админ Тестов",
        "role": UserRole.ADMIN,
    },
]


async def seed_users():
    async with async_session() as db:
        for user_data in TEST_USERS:
            existing = await db.execute(
                select(User).where(User.email == user_data["email"])
            )
            if existing.scalar_one_or_none():
                print(f"Пользователь {user_data['email']} уже существует")
                continue

            user = User(
                email=user_data["email"],
                hashed_password=hash_password(user_data["password"]),
                name=user_data["name"],
                role=user_data["role"],
            )
            db.add(user)
            print(f"Создан: {user_data['email']} ({user_data['role'].value})")

        await db.commit()
        print("База данных успешно наполнена тестовыми пользователями.")


if __name__ == "__main__":
    asyncio.run(seed_users())
