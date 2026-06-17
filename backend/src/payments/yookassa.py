import uuid

from yookassa import Configuration, Payment

from src.core.config import settings
from src.payments.base import BasePaymentProvider, PaymentResult, PaymentStatus


class YookassaProvider(BasePaymentProvider):
    """Реализация платёжного провайдера через ЮКассу."""

    def __init__(self) -> None:
        Configuration.account_id = settings.YOOKASSA_SHOP_ID
        Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

    async def create_payment(
        self,
        amount: int,
        order_id: int,
        description: str,
        save_payment_method: bool = False,
        payment_method_id: str | None = None,
        payment_type: str = "card",
    ) -> PaymentResult:
        """Создать платёж в ЮКассе."""

        payment_data: dict = {
            "amount": {
                "value": f"{amount / 100:.2f}",  # Копейки конвертируем в рубли
                "currency": "RUB",
            },
            "description": description,
            "metadata": {"order_id": order_id},
            "capture": True,
        }

        if payment_method_id:
            # Автосписание с сохранённой карты
            payment_data["payment_method_id"] = payment_method_id
        else:
            # Обычная оплата с возможностью привязки карты
            payment_data["confirmation"] = {
                "type": "embedded",
            }
            payment_data["return_url"] = settings.YOOKASSA_RETURN_URL

            if payment_type == "sbp":
                payment_data["payment_method_data"] = {"type": "sbp"}

        payment = Payment.create(payment_data, str(uuid.uuid4()))

        confirmation_url = ""
        confirmation_token = None

        if hasattr(payment, "confirmation") and payment.confirmation:
            # При embedded - только токен, url нет
            confirmation_token = payment.confirmation.confirmation_token
            # При redirect - только url, токена нет
            confirmation_url = getattr(payment.confirmation, "confirmation_url", "")

        return PaymentResult(
            payment_id=payment.id,
            confirmation_url=confirmation_url,
            confirmation_token=confirmation_token,
            status=payment.status,
        )

    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """Получить статус платежа из ЮКассы."""
        payment = Payment.find_one(payment_id)

        method_id = None
        method_title = None

        if payment.payment_method and payment.payment_method.saved:
            method_id = payment.payment_method.id
            if hasattr(payment.payment_method, "card"):
                last4 = payment.payment_method.card.last4
                method_title = f"•••• {last4}"

        return PaymentStatus(
            payment_id=payment.id,
            status=payment.status,
            paid=payment.paid,
            payment_method_id=method_id,
            payment_method_title=method_title,
        )
