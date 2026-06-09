from pydantic import BaseModel, EmailStr, Field, field_validator

from src.models.user import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    email: EmailStr = Field(..., description="Электронная почта пользователя")
    name: str | None = Field(None, max_length=100, description="Имя пользователя")
    phone: str | None = Field(None, description="Номер телефона")


class UserCreate(UserBase):
    """Схема для валидации данных при регистрации нового пользователя."""

    password: str = Field(..., min_length=6, max_length=30, description="Пароль")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        """Проверка, что телефон состоит из цифр и спецсимволов."""
        if v is not None:
            clean_phone = "".join(c for c in v if c.isdigit())
            if len(clean_phone) < 10:
                raise ValueError("Номер телефона должен содержать минимум 10 цифр")
        return v


class UserLogin(BaseModel):
    """Схема для валидации данных при входе в систему."""

    email: EmailStr = Field(..., description="Электронная почта")
    password: str = Field(..., description="Пароль")


class UserResponse(UserBase):
    """Схема для безопасного возврата данных пользователя на фронтенд.

    Пароль здесь отсутствует.
    """

    id: int = Field(..., description="Уникальный идентификатор")
    role: UserRole = Field(..., description="Роль пользователя на сайте")

    class ConfigDict:
        # Pydantic настройка для чтения данных из ORM-моделей
        from_attributes = True


class TokenResponse(BaseModel):
    """Схема ответа сервера при успешном входе в систему."""

    access_token: str = Field(..., description="Цифровой пропуск (JWT токен)")
    token_type: str = Field("bearer", description="Тип токена")


class UserUpdate(BaseModel):
    """Схема для частичного обновления профиля пользователя (PATCH).

    Все поля опциональны. Обновляются только те, что переданы в запросе.
    """

    name: str | None = Field(None, max_length=100, description="Новое имя пользователя")
    phone: str | None = Field(None, description="Новый номер телефона")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        """Проверяет, что номер содержит не менее 10 цифр."""
        if v is not None:
            clean_phone = "".join(c for c in v if c.isdigit())
            if len(clean_phone) < 10:
                raise ValueError("Номер телефона должен содержать минимум 10 цифр")
        return v
