import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class UserSession(Base):
    """Модель для хранения долгоживущих Refresh-сессий пользователей."""

    __tablename__ = "user_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Refresh-токен храним в виде уникальной UUID строки
    refresh_token: Mapped[str] = mapped_column(
        String(255), unique=True, default=lambda: str(uuid.uuid4()), index=True
    )

    # Срок действия токена
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Время создания сессии
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    # Связь с моделью пользователя
    user = relationship("User", backref="sessions")
