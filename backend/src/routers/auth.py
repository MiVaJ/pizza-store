import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.core.security import (
    create_access_token,
    get_session_lifetime,
    hash_password,
    set_auth_cookies,
    verify_password,
)
from src.models.session import UserSession
from src.models.user import User
from src.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate

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


@router.post(
    "/login",
    response_model=None,
    summary="Вход в систему (Выдача кук)",
    description=(
        "Аутентификация пользователя по JSON-данным. "
        "Генерирует короткий Access-токен и создает в базе данных "
        "Refresh-сессию с динамическим временем жизни на основе роли."
    ),
)
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

    await db.execute(delete(UserSession).where(UserSession.user_id == user.id))

    # 3. Создаём короткий Access-токен
    token_data = {"sub": str(user.id)}
    access_token = create_access_token(data=token_data)

    # 4. Генерируем и сохраняем Refresh-сессию в БД
    session_time = get_session_lifetime(user.role)
    expires_at_date = datetime.now(timezone.utc) + timedelta(seconds=session_time)
    refresh_token_value = str(uuid.uuid4())

    new_session = UserSession(
        user_id=user.id, refresh_token=refresh_token_value, expires_at=expires_at_date
    )
    db.add(new_session)
    await db.commit()

    # 5. Устанавливаем все куки
    set_auth_cookies(
        response=response,
        user_id=user.id,
        role=user.role,
        access_token=access_token,
        refresh_token=refresh_token_value,
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

    # 5. Генерируем новые токены и сессию
    token_data = {"sub": str(user.id)}
    new_access_token = create_access_token(data=token_data)
    new_refresh_token_value = str(uuid.uuid4())

    session_time = get_session_lifetime(user.role)
    new_expires_at = datetime.now(timezone.utc) + timedelta(seconds=session_time)

    # 6. Записываем новую сессию в БД
    new_session = UserSession(
        user_id=user.id,
        refresh_token=new_refresh_token_value,
        expires_at=new_expires_at,
    )
    db.add(new_session)
    await db.commit()

    # 7. Устанавливаем все куки
    set_auth_cookies(
        response=response,
        user_id=user.id,
        role=user.role,
        access_token=new_access_token,
        refresh_token=new_refresh_token_value,
    )

    return {"detail": "Токены успешно обновлены"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Профиль текущего пользователя",
    description=(
        "Возвращает данные авторизованного пользователя по Access-куке. "
        "Используется для отображения страницы профиля и инициализации "
        "состояния пользователя на фронтенде."
    ),
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> User:
    """Возвращает профиль текущего авторизованного пользователя."""
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
    summary="Обновление профиля",
    description=(
        "Обновляет имя и номер телефона авторизованного пользователя. "
        "Все поля опциональны — передавай только то, что нужно изменить. "
        "Проверяет уникальность нового номера телефона среди других пользователей."
    ),
)
async def update_me(
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Частичное обновление профиля (PATCH).

    Обновляет только переданные поля, остальные остаются без изменений.
    Перед сохранением телефона проверяет его уникальность в базе.
    """
    # 1. Если передан телефон, то проверяем, не занят ли он другим пользователем
    if user_data.phone is not None:
        existing = await db.execute(
            select(User).where(
                User.phone == user_data.phone,
                User.id != current_user.id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Этот номер телефона уже используется другим пользователем",
            )

    # 2. Обновляем только переданные поля
    if user_data.name is not None:
        current_user.name = user_data.name
    if user_data.phone is not None:
        current_user.phone = user_data.phone

    # 3. Фиксируем изменения и возвращаем обновлённый объект
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.post(
    "/logout",
    summary="Выход из системы",
    description="Удаляет Access и Refresh куки и инвалидирует сессию в базе данных.",
)
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Выход из системы. Удаляет сессию из БД и очищает куки."""
    refresh_token = request.cookies.get("fastapi_refresh")

    if refresh_token:
        await db.execute(
            delete(UserSession).where(UserSession.refresh_token == refresh_token)
        )
        await db.commit()

    response.delete_cookie("fastapi_access")
    response.delete_cookie("fastapi_refresh")

    return {"detail": "Вы успешно вышли из системы"}