from passlib.context import CryptContext

# Контекст шифрования (алгоритм bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Принимает чистый пароль и возвращает его криптографический хеш."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Сравнивает чистый пароль от пользователя с хешем из базы данных.

    Возвращает True, если они совпадают, иначе False.
    """
    return pwd_context.verify(plain_password, hashed_password)
