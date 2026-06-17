import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class OrderStatus(str, enum.Enum):
    """Статусы выполнения заказа для курьера, кухни и клиента."""

    PENDING = "pending"  # ожидает оплаты / обработки
    COOKING = "cooking"  # готовится на кухне
    DELIVERING = "delivering"  # передан курьеру, в пути
    COMPLETED = "completed"  # успешно доставлен и закрыт
    CANCELLED = "cancelled"  # отменен


class Order(Base):
    """Главная модель заказа (информация о доставке и итоговом чеке)."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Ссылка на пользователя. Позволяет создавать заказы от гостевых пользвоателей
    # Если пользователь будет удалён, то заказ автоматически станет гостевым
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    # Данные клиента для доставки
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    delivery_address: Mapped[str] = mapped_column(String(500), nullable=False)

    # Финансовые и временные поля
    total_price: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False
    )
    # ID платежа в платёжной системе
    payment_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Связи: один заказ содержит внутри себя много строчек купленных товаров
    items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base):
    """Модель конкретного товара внутри заказа (отдельная строчка в чеке)."""

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )

    # Ссылки на пиццу или соус из меню базы данных.
    pizza_id: Mapped[int | None] = mapped_column(
        ForeignKey("pizzas.id", ondelete="SET NULL"), nullable=True
    )
    ingredient_id: Mapped[int | None] = mapped_column(
        ForeignKey("ingredients.id", ondelete="SET NULL"), nullable=True
    )

    # Фиксируем название и цену на момент покупки
    product_name: Mapped[str] = mapped_column(String(150), nullable=False)
    price_at_purchase: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Обратная связь с главным родительским заказом
    order: Mapped["Order"] = relationship("Order", back_populates="items")
