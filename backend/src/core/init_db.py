from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.security import hash_password
from src.models.user import User, UserRole


async def create_initial_admin(db: AsyncSession) -> None:
    """Автоматически создает дефолтного администратора при первом запуске бэкенда."""
    admin_email = "admin@pizzatut.ru"

    # Проверяем, существует ли уже администратор в базе
    result = await db.execute(select(User).where(User.email == admin_email))
    admin_exists = result.scalar_one_or_none()

    # Если администратора ещё нет, то создаём его
    if not admin_exists:
        new_admin = User(
            email=admin_email,
            name="Главный Admin",
            hashed_password=hash_password("admin123"),
            role=UserRole.ADMIN,
        )
        db.add(new_admin)
        await db.commit()
        print("Создан дефолтный администратор:")
        print(f"Email: {admin_email} | Password: admin123")
