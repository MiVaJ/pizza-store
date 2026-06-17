from pydantic import BaseModel, Field


class CreatePaymentRequest(BaseModel):
    """Схема запроса на создание платежа для заказа."""

    order_id: int = Field(..., description="ID заказа")
    save_card: bool = Field(False, description="Привязать карту к аккаунту")
    use_saved_card: bool = Field(False, description="Оплатить сохранённой картой")
    payment_type: str = Field("card", description="Тип оплаты: card, sbp, saved")


class PaymentResponse(BaseModel):
    """Схема ответа с данными созданного платежа."""

    payment_id: str = Field(..., description="ID платежа в системе провайдера")
    confirmation_url: str = Field(..., description="URL для редиректа на оплату")
    status: str = Field(..., description="Статус платежа")
    confirmation_token: str | None = Field(
        None, description="Токен для инициализации виджета ЮКассы"
    )


class SavedCardResponse(BaseModel):
    """Схема получения информации о привязанной карте пользователя."""

    has_saved_card: bool = Field(
        ..., description="Есть ли привязанная карта у пользователя"
    )
    card_title: str | None = Field(
        None, description="Отображаемое название карты, например '•••• 4242'"
    )
