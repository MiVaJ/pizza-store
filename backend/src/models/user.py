import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.core.database import Base


class UserRole(str, enum.Enum):
    CLIENT = "client"
    MANAGER = "manager"
    COURIER = "courier"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(
        String(150), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=True)

    # Роль пользователя по умолчанию - клиент
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole), default=UserRole.CLIENT, nullable=False
    )
