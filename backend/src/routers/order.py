from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.database import get_db
from src.models.ingredient import Ingredient
from src.models.order import Order, OrderItem, OrderStatus
from src.models.pizza import Pizza
from src.schemas.order import OrderCreate, OrderResponse

router = APIRouter(prefix="/api/orders", tags=["Заказы"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order_data: OrderCreate, db: AsyncSession = Depends(get_db)):
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
        user_id=None,
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
