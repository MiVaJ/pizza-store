from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PaymentResult:
    """Результат создания платежа."""

    payment_id: str  # ID платежа в системе провайдера
    confirmation_url: str  # URL куда редиректить пользователя для оплаты
    status: str  # pending / succeeded / cancelled


@dataclass
class PaymentStatus:
    """Статус существующего платежа."""

    payment_id: str
    status: str
    paid: bool
    payment_method_id: str | None = None  # ID сохранённой карты
    payment_method_title: str | None = None  # Название карты "**** 4242"


class BasePaymentProvider(ABC):
    """Абстрактный провайдер платежей."""

    @abstractmethod
    async def create_payment(
        self,
        amount: int,  # сумма в копейках
        order_id: int,
        description: str,
        save_payment_method: bool = False,  # True - привязать карту
        payment_method_id: str | None = None,  # ID сохранённой карты для автосписания
    ) -> PaymentResult:
        """Создать новый платёж и получить ссылку для оплаты."""
        ...

    @abstractmethod
    async def get_payment_status(self, payment_id: str) -> PaymentStatus:
        """Получить текущий статус платежа по ID."""
        ...
