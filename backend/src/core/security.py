from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from src.core.config import settings

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
