import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.core.database import get_db
from src.core.security import ALGORITHM, SECRET_KEY
from src.models.user import User, UserRole


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Зависимость для аутентификации пользователя по HttpOnly Cookies."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Вы не авторизованы в системе",
        headers={"WWW-Authenticate": "Cookie"},
    )

    # Достаём токен из кук браузера
    token = request.cookies.get("fastapi_access")
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = int(user_id_str)
    except (jwt.PyJWTError, ValueError):
        raise credentials_exception from None

    # Ищем пользователя в БД по ID
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Возвращает пользователя, если авторизован, None если гость."""
    token = request.cookies.get("fastapi_access")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        user_id = int(user_id_str)
    except (jwt.PyJWTError, ValueError):
        return None
    # Ищем пользователя в БД по ID
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    return user


class RoleChecker:
    """Класс-фабрика для проверки ролей."""

    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен: недостаточно прав для этого действия.",
            )
        return current_user


allow_management = RoleChecker([UserRole.ADMIN, UserRole.MANAGER])
