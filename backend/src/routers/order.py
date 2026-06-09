from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import get_db
from src.core.dependencies import allow_management, get_optional_user
from src.models.ingredient import Ingredient
from src.models.order import Order, OrderItem, OrderStatus
from src.models.pizza import Pizza
from src.models.user import User
from src.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate

router = APIRouter(prefix="/api/orders", tags=["Заказы"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    """Оформление нового заказа."""

    # 1. Извлекаем все ID пицц и ингредиентов
    pizza_ids = [
        item.pizza_id for item in order_data.items if item.pizza_id is not None
    ]
    ingredient_ids = [
        item.ingredient_id
        for item in order_data.items
        if item.ingredient_id is not None
    ]

    # 2. Делаем запросы в БД
    db_pizzas = {}
    if pizza_ids:
        pizza_query = select(Pizza).where(Pizza.id.in_(pizza_ids))
        pizza_result = await db.execute(pizza_query)
        db_pizzas = {p.id: p for p in pizza_result.scalars().all()}

    db_ingredients = {}
    if ingredient_ids:
        ing_query = select(Ingredient).where(Ingredient.id.in_(ingredient_ids))
        ing_result = await db.execute(ing_query)
        db_ingredients = {i.id: i for i in ing_result.scalars().all()}

    # 3. Считаем общую стоимость чека
    order_items = []
    calculated_total_price = 0

    for item in order_data.items:
        if item.pizza_id is not None:
            db_pizza = db_pizzas.get(item.pizza_id)
            if not db_pizza:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Пицца с ID {item.pizza_id} не найдена в меню ресторана",
                )
            product_name = db_pizza.name
            price_at_purchase = db_pizza.price

        elif item.ingredient_id is not None:
            db_sauce = db_ingredients.get(item.ingredient_id)
            if not db_sauce:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Соус с ID {item.ingredient_id} не найден в меню ресторана",
                )
            product_name = db_sauce.name
            price_at_purchase = db_sauce.price
        else:
            continue

        calculated_total_price += price_at_purchase * item.quantity

        order_item = OrderItem(
            pizza_id=item.pizza_id,
            ingredient_id=item.ingredient_id,
            product_name=product_name,
            price_at_purchase=price_at_purchase,
            quantity=item.quantity,
        )
        order_items.append(order_item)

    # 4. Создаем объект заказа
    new_order = Order(
        user_id=current_user.id if current_user else None,
        customer_name=order_data.customer_name,
        phone=order_data.phone,
        delivery_address=order_data.delivery_address,
        total_price=calculated_total_price,
        status=OrderStatus.PENDING,
        items=order_items,
    )

    db.add(new_order)
    await db.commit()

    query = (
        select(Order).where(Order.id == new_order.id).options(selectinload(Order.items))
    )
    result = await db.execute(query)
    saved_order = result.scalar_one()

    return saved_order


@router.get("/", response_model=list[OrderResponse], status_code=status.HTTP_200_OK)
async def get_orders_history(db: AsyncSession = Depends(get_db)):
    """Получение истории всех оформленных заказов."""

    # Делаем запрос ко всем заказам и сортируем по дате создания
    query = (
        select(Order)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )

    result = await db.execute(query)
    orders = result.scalars().all()

    return orders


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Обновить статус заказа (Доступно: ADMIN, MANAGER)",
    description="Доступно только для персонала.",
)
async def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(allow_management),
):
    """Доступ к изменению статуса заказа менеджером или админом."""
    # 1. Делаем запрос к БД на получение заказа по ID
    query = (
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items))
        .with_for_update()
    )
    result = await db.execute(query)
    order = result.scalar_one_or_none()

    # 2. Если заказ не найден
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Заказ №{order_id} не найден в системе",
        )

    # 3. Запускаем валидацию переходов состояний из схемы
    try:
        status_data.validate_transition(current_status=order.status)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        ) from None

    # 4. Обновляем статус и фиксируем изменения в БД
    order.status = status_data.status

    await db.commit()
    await db.refresh(order)

    return order
