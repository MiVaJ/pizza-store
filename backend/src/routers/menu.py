from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.redis import get_cached_menu, get_redis_client, set_cached_menu
from src.models.pizza import Pizza
from src.schemas.pizza import PizzaResponse

router = APIRouter(prefix="/api/menu", tags=["Меню пиццерии"])


@router.get("/", response_model=list[PizzaResponse])
async def get_menu(db: AsyncSession = Depends(get_db)) -> list[dict]:
    """Получение списка всех доступных пицц для отображения на сайте.
    Результат кэшируется в Redis на 10 минут.
    """
    redis = get_redis_client()

    try:
        # 1. Сначала пробуем получить данные из кэша
        cached = await get_cached_menu(redis)
        if cached is not None:
            return cached

        # 2. Если кэш пуст, то делаем запрос в БД
        # Выбираем только те пиццы, которые сейчас есть в наличии
        query = select(Pizza).where(Pizza.is_available.is_(True)).order_by(Pizza.id)
        result = await db.execute(query)
        pizzas = result.scalars().all()

        # 3. Сериализуем и сохраняем в кэш
        pizzas_data = [
            PizzaResponse.model_validate(p).model_dump(mode="json") for p in pizzas
        ]
        await set_cached_menu(redis, pizzas_data)

        return pizzas_data

    finally:
        await redis.aclose()
