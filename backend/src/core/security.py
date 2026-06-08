from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Response

from src.core.config import settings
from src.models.user import UserRole

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


def hash_password(password: str) -> str:
    """Принимает чистый текст пароля и возвращает его криптографический хеш."""
    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Сравнивает чистый пароль от пользователя с хешем из базы данных."""
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Создает временный JWT-токен для пользователя с динамическим временем жизни."""
    to_encode = data.copy()

    # Выбираем время жизни токена
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    # Добавляем время истечения в данные токена
    to_encode.update({"exp": expire})

    # Запекаем данные и подписываем их секретным ключом
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_session_lifetime(role: UserRole) -> int:
    """Рассчитывает время жизни Refresh-сессии в секундах."""
    if role in [UserRole.ADMIN, UserRole.MANAGER, UserRole.COURIER]:
        return 3600 * 12  # Персонал: 12 часов
    return 3600 * 24 * 30  # Клиенты: 30 дней


def set_auth_cookies(
    response: Response,
    user_id: int,
    role: UserRole,
    access_token: str,
    refresh_token: str,
) -> None:
    """Универсальная утилита для установки Access и Refresh кук."""
    # 1. Устанавливаем короткую Access-куку (15 минут)
    response.set_cookie(
        key="fastapi_access",
        value=access_token,
        httponly=True,
        secure=False,  # Не забыть выставить True на продакшне для HTTPS
        samesite="lax",
        max_age=15 * 60,
    )

    # 2. Получаем динамическое время жизни для Refresh-куки
    session_time = get_session_lifetime(role)

    # 3. Запекаем новый рефреш в куку
    response.set_cookie(
        key="fastapi_refresh",
        value=refresh_token,
        httponly=True,
        secure=False,  # Не забыть выставить True на продакшне для HTTPS
        samesite="lax",
        max_age=session_time,
    )
