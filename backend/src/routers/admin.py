from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import allow_admin
from src.models.user import User, UserRole
from src.schemas.user import UserResponse

router = APIRouter(prefix="/api/admin", tags=["Админ панель"])


class RoleUpdate(BaseModel):
    role: UserRole = Field(..., description="Новая роль пользователя")


@router.get(
    "/users",
    response_model=list[UserResponse],
    summary="Список всех пользователей",
    description="Доступно только для администратора.",
)
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_admin),
) -> list[User]:
    """Возвращает список всех пользователей системы."""
    result = await db.execute(select(User).order_by(User.id))
    return list(result.scalars().all())


@router.patch(
    "/users/{user_id}/role",
    response_model=UserResponse,
    summary="Изменить роль пользователя",
    description="Доступно только для администратора. Нельзя изменить роль самому себе.",
)
async def update_user_role(
    user_id: int,
    role_data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_admin),
) -> User:
    """Меняет роль пользователя по ID."""

    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя изменить собственную роль",
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден",
        )

    user.role = role_data.role
    await db.commit()
    await db.refresh(user)
    return user
