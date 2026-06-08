from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)

from src.models.order import OrderStatus
from src.schemas.pizza import RublesInt


class OrderItemCreate(BaseModel):
    """Схема для валидации одной строчки товара."""

    # Получаем ID Пиццы или Ингредиента
    pizza_id: int | None = Field(None, description="ID выбранной пиццы")
    ingredient_id: int | None = Field(None, description="ID выбранного соуса")

    # Получаем количество
    quantity: int = Field(..., description="Количество", ge=1)

    # Проверяем, что в строке корзины есть хотя бы один товар
    @model_validator(mode="after")
    def check_product_presence(self) -> "OrderItemCreate":
        # self — это уже собранный объект строки чека
        if self.pizza_id is None and self.ingredient_id is None:
            raise ValueError(
                "В строке заказа должен быть указан либо ID пиццы, либо ID соуса"
            )
        return self


class OrderCreate(BaseModel):
    """Схема для валидации всей формы оформления заказа."""

    customer_name: str = Field(
        ..., description="Имя получателя", min_length=2, max_length=100
    )
    phone: str = Field(..., description="Номер телефона")
    delivery_address: str = Field(..., description="Полный адрес доставки пиццы")

    # Массив элементов корзины
    items: list[OrderItemCreate] = Field(
        ..., description="Список всех элементов в чеке"
    )

    # Очищаем и проверяем номер телефона
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        clean_phone = "".join(c for c in v if c.isdigit())
        if len(clean_phone) < 10:
            raise ValueError("Номер телефона должен содержать минимум 10 цифр")
        return v

    # Проверяем, что адрес заполнен и содержит достаточно информации
    @field_validator("delivery_address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        """Проверяем, что адрес содержит буквы и хотя бы одну цифру."""
        clean_address = v.strip()

        if not clean_address:
            raise ValueError("Адрес доставки не может быть пустым")

        letters_count = sum(c.isalpha() for c in clean_address)
        if letters_count < 4:
            raise ValueError("Пожалуйста, укажите название улицы в адресе доставки")
        # Проверяем, ввел ли пользователь цифру
        has_digit = any(c.isdigit() for c in clean_address)
        if not has_digit:
            raise ValueError("Пожалуйста, укажите номер дома в адресе доставки")

        return clean_address

    # Защищаем систему от попыток отправить заказ с пустой корзиной
    @field_validator("items")
    @classmethod
    def validate_items_not_empty(
        cls, v: list[OrderItemCreate]
    ) -> list[OrderItemCreate]:
        if not v:
            raise ValueError("Корзина заказа не может быть пустой")
        return v


class OrderItemResponse(BaseModel):
    """Схема для отдачи строчки купленного товара."""

    id: int = Field(..., description="Уникальный ID строки чека")
    pizza_id: int | None = Field(None, description="ID пиццы")
    ingredient_id: int | None = Field(None, description="ID соуса")
    product_name: str = Field(..., description="Название товара на момент покупки")
    price_at_purchase: RublesInt = Field(..., description="Стоимость в рублях")
    quantity: int = Field(..., description="Количество")

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Схема для отдачи полной информации о заказе."""

    id: int = Field(..., description="ID заказа в системе")
    customer_name: str = Field(..., description="Имя получателя")
    phone: str = Field(..., description="Номер телефона")
    delivery_address: str = Field(..., description="Адрес доставки")
    total_price: RublesInt = Field(..., description="Итоговая сумма чека")
    status: OrderStatus = Field(..., description="Текущий статус заказа")
    created_at: datetime = Field(..., description="Точная дата и время создания заказа")
    items: list[OrderItemResponse] = Field(
        default=[], description="Развернутый список купленных товаров"
    )

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Схема для валидации изменения статуса заказа менеджером или админом."""

    status: OrderStatus = Field(..., description="Новый статус заказа")

    def validate_transition(self, current_status: OrderStatus) -> None:
        """Валидация разрешенных переходов между статусами."""
        # Если статус не меняется - это валидно
        if current_status == self.status:
            return

        # Разрешённые переходы
        allowed_transitions = {
            OrderStatus.PENDING: [OrderStatus.COOKING, OrderStatus.CANCELLED],
            OrderStatus.COOKING: [OrderStatus.DELIVERING, OrderStatus.CANCELLED],
            OrderStatus.DELIVERING: [OrderStatus.COMPLETED, OrderStatus.CANCELLED],
            # Финальные статусы менять нельзя
            OrderStatus.COMPLETED: [],
            OrderStatus.CANCELLED: [],
        }

        valid_next_statuses = allowed_transitions.get(current_status, [])

        if self.status not in valid_next_statuses:
            allowed_names = [s.value for s in valid_next_statuses]
            raise ValueError(
                f"Невозможно перевести заказ из '{current_status.value}' "
                f"в '{self.status.value}'. Допустимы: {allowed_names or 'нет'}"
            )
