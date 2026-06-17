from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.dependencies import get_current_user
from src.models.order import Order, OrderStatus
from src.models.user import User
from src.payments.schemas import (
    CreatePaymentRequest,
    PaymentResponse,
    SavedCardResponse,
)
from src.payments.yookassa import YookassaProvider

router = APIRouter(prefix="/api/payments", tags=["Платежи"])


def get_payment_provider() -> YookassaProvider:
    """Зависимость для получения платёжного провайдера."""
    return YookassaProvider()


@router.get(
    "/saved-card",
    response_model=SavedCardResponse,
    summary="Информация о привязанной карте",
    description=(
        "Возвращает информацию о сохранённой карте текущего пользователя."
        "Если карта не привязана, то возвращает has_saved_card: false."
    ),
)
async def get_saved_card(
    current_user: User = Depends(get_current_user),
) -> SavedCardResponse:
    """Возвращает информацию о сохранённой карте пользователя."""
    return SavedCardResponse(
        has_saved_card=current_user.payment_method_id is not None,
        card_title=current_user.payment_method_title,
    )


@router.post(
    "/create",
    response_model=PaymentResponse,
    summary="Создать платёж для заказа",
    description=(
        "Создаёт платёж в ЮКассе для указанного заказа."
        "Возвращает ссылку для редиректа на страницу оплаты."
        "Если карта привязана, то выполняется без редиректа"
    ),
)
async def create_payment(
    data: CreatePaymentRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    provider: YookassaProvider = Depends(get_payment_provider),
) -> PaymentResponse:
    """Создаёт платёж в ЮКассе и возвращает ссылку для оплаты."""

    # 1. Проверяем что заказ существует и принадлежит пользователю
    query = select(Order).where(
        Order.id == data.order_id,
        Order.user_id == current_user.id,
    )
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ №{data.order_id} не найден",
        )

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Оплатить можно только заказ со статусом pending",
        )

    # 2. Определяем метод оплаты
    payment_method_id = None
    if data.use_saved_card and current_user.payment_method_id:
        payment_method_id = current_user.payment_method_id

    # 3. Создаём платёж
    payment_result = await provider.create_payment(
        amount=order.total_price,
        order_id=order.id,
        description=f"Оплата заказа №{order.id} в ПиццаТут",
        save_payment_method=data.save_card,
        payment_method_id=payment_method_id,
    )

    # 4. Сохраняем payment_id в заказе
    order.payment_id = payment_result.payment_id
    await db.commit()

    return PaymentResponse(
        payment_id=payment_result.payment_id,
        confirmation_url=payment_result.confirmation_url,
        status=payment_result.status,
    )


@router.post(
    "/webhook",
    summary="Webhook от ЮКассы",
    description="Принимает уведомления об изменении статуса платежа.",
)
async def payment_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    provider: YookassaProvider = Depends(get_payment_provider),
) -> dict:
    """Обрабатывает webhook от ЮКассы при успешной оплате."""

    body = await request.json()
    event = body.get("event")
    payment_id = body.get("object", {}).get("id")

    if not payment_id or event != "payment.succeeded":
        return {"status": "ignored"}

    # 1. Получаем статус платежа из ЮКассы
    payment_status = await provider.get_payment_status(payment_id)

    if not payment_status.paid:
        return {"status": "not paid"}

    # 2. Находим заказ по payment_id
    query = select(Order).where(Order.payment_id == payment_id)
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    if not order:
        return {"status": "order not found"}

    # 3. Обновляем статус заказа
    order.status = OrderStatus.COOKING

    # 4. Если карта была сохранена, то привязываем к пользователю
    if payment_status.payment_method_id and order.user_id:
        user_query = select(User).where(User.id == order.user_id)
        user_result = await db.execute(user_query)
        user = user_result.scalar_one_or_none()

        if user:
            user.payment_method_id = payment_status.payment_method_id
            user.payment_method_title = payment_status.payment_method_title

    await db.commit()

    return {"status": "ok"}
