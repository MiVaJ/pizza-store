from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import create_access_token, hash_password, verify_password
from src.models.user import User
from src.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse

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


@router.post("/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin, db: AsyncSession = Depends(get_db)) -> dict:
    """Вход в систему.

    Проверяет пароль и выдает JWT-токен.
    """
    # 1. Ищем пользователя в базе данных по почте
    query = select(User).where(User.email == login_data.email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    # 2. Если пользователя нет или пароль не совпал - выдаём ошибку
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверная электронная почта или пароль",
        )

    # 3. Зашиваем в токен базовые данные пользователя
    token_data = {"sub": str(user.id), "role": user.role}

    # 4. Генерируем токен
    token = create_access_token(data=token_data)

    return {"access_token": token, "token_type": "bearer"}
