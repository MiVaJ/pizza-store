import json
from typing import Any

from redis.asyncio import Redis

from src.core.config import settings

# Время жизни кэша меню
MENU_CACHE_TTL = 60 * 10
MENU_CACHE_KEY = "menu:pizzas"


def get_redis_client() -> Redis:
    """Создаёт async Redis-клиент из настроек."""
    return Redis.from_url(settings.REDIS_URL, decode_responses=True)


async def get_cached_menu(redis: Redis) -> list[dict[str, Any]] | None:
    """Возвращает закэшированное меню или None если кэш пуст/устарел."""
    cached = await redis.get(MENU_CACHE_KEY)
    if cached:
        return json.loads(cached)
    return None


async def set_cached_menu(redis: Redis, pizzas: list[dict[str, Any]]) -> None:
    """Сохраняет меню в кэш на 10 минут."""
    await redis.set(
        MENU_CACHE_KEY, json.dumps(pizzas, ensure_ascii=False), ex=MENU_CACHE_TTL
    )


async def invalidate_menu_cache(redis: Redis) -> None:
    """Сбрасывает кэш меню. Вызывать при изменении состава пицц."""
    await redis.delete(MENU_CACHE_KEY)
