from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import hash_password
from src.models.user import User
from src.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/api/auth", tags=["Авторизация"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate, db: AsyncSession = Depends(get_db)
) -> User:
    """
    Регистрация нового пользователя на сайте.

    Принимает почту и пароль, проверяет дубликаты,
    шифрует пароль и сохраняет пользователя в базу данных.
    """
    # 1. Проверяем, нет ли уже пользователя с такой почтой в базе
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с такой электронной почтой уже зарегистрирован",
        )

    # 2. Хешируем пароль
    secured_password = hash_password(user_data.password)

    # 3. Создаем новый объект пользователя для базы данных
    new_user = User(
        email=user_data.email,
        hashed_password=secured_password,
        name=user_data.name,
        phone=user_data.phone,
    )

    # 4. Сохраняем в БД
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
