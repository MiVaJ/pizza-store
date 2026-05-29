from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.pizza import Pizza
from src.schemas.pizza import PizzaResponse

router = APIRouter(prefix="/api/menu", tags=["Меню пиццерии"])


@router.get("/", response_model=list[PizzaResponse])
async def get_menu(db: AsyncSession = Depends(get_db)) -> list[Pizza]:
    """Получение списка всех доступных пицц для отображения на сайте."""
    # Выбираем только те пиццы, которые сейчас есть в наличии
    query = select(Pizza).where(Pizza.is_available.is_(True)).order_by(Pizza.id)
    result = await db.execute(query)
    pizzas = result.scalars().all()

    return list(pizzas)
