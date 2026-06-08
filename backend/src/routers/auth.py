import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import create_access_token, hash_password, verify_password
from src.models.session import UserSession
from src.models.user import User, UserRole
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
async def login_user(
    login_data: UserLogin, response: Response, db: AsyncSession = Depends(get_db)
) -> dict:
    """Вход в систему.

    Проверяет пароль, выдает JWT-токен и запекает его в куку.
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

    # 3. Динамически рассчитываем время жизни сессии
    if user.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.COURIER]:
        # Сессия для персонала на рабочую смену (12 часов)
        session_time = 3600 * 12
    else:
        # Сессия для клиентов на месяц
        session_time = 3600 * 24 * 30

    # 4. Создаём короткий Access-токен и запекаем для него куку
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(data=token_data)

    response.set_cookie(
        key="fastapi_access",
        value=access_token,
        httponly=True,
        secure=False,  # Не забыть выставить True на продакшне для HTTPS
        samesite="lax",
        max_age=15 * 60,
    )

    # 5. Рассчитываем точную дату окончания жизни куки
    expires_at_date = datetime.now(timezone.utc) + timedelta(seconds=session_time)

    # 6. Создаём долгоживущую Refresh-сессию
    refresh_token_value = str(uuid.uuid4())
    new_session = UserSession(
        user_id=user.id, refresh_token=refresh_token_value, expires_at=expires_at_date
    )
    db.add(new_session)
    await db.commit()

    # 7. Формируем долгоживуюущую куку
    response.set_cookie(
        key="fastapi_token",
        value=refresh_token_value,
        httponly=True,
        secure=False,  # Не забыть выставитьTrue на продакшне для HTTPS
        samesite="lax",
        max_age=session_time,
    )
    return {"detail": "Успешный вход в систему"}


@router.post(
    "/refresh",
    summary="Обновить токены сессии",
    description="Бесшумно обновляет Access и Refresh куки",
)
async def refresh_tokens(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Обновление сессии (Refresh).

    Читает рефреш-куку, проверяет БД, удаляет старую сессию
    и выдает новую пару кук (Access + Refresh).
    """
    # 1. Извлекаем старый рефреш-токен из кук
    old_refresh_token = request.cookies.get("fastapi_refresh")
    if not old_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствует токен обновления",
        )

    # 2. Ищем сессию в БД вместе с пользователем
    from sqlalchemy.orm import selectinload

    query = (
        select(UserSession)
        .where(UserSession.refresh_token == old_refresh_token)
        .options(selectinload(UserSession.user))
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()

    # 3. Если сессии нет или она просрочена, то разлогиниваем пользователя
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен обновления",
        )

    if session.expires_at < datetime.now(timezone.utc):
        await db.delete(session)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия сессии истек",
        )

    user = session.user

    # 4. Удаляем старую сессию
    await db.delete(session)

    # 5. Генерируем новый короткий Access-токен
    token_data = {"sub": str(user.id)}
    new_access_token = create_access_token(data=token_data)

    response.set_cookie(
        key="fastapi_access",
        value=new_access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=15 * 60,
    )

    # 6. Рассчитываем время для новой сессии
    if user.role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.COURIER]:
        session_seconds = 3600 * 12
    else:
        session_seconds = 3600 * 24 * 30

    new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=session_seconds)
    new_refresh_token_value = str(uuid.uuid4())

    # 7. Записываем новую сессию в БД
    new_session = UserSession(
        user_id=user.id,
        refresh_token=new_refresh_token_value,
        expires_at=new_expires_at,
    )
    db.add(new_session)
    await db.commit()

    # 8. Запекаем новый рефреш в куку
    response.set_cookie(
        key="fastapi_refresh",
        value=new_refresh_token_value,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=session_seconds,
    )

    return {"detail": "Токены успешно обновлены"}
