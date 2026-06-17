import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings
from src.models.order import Order, OrderStatus
from src.models.session import UserSession  # noqa: F401
from src.models.user import User  # noqa: F401
from src.worker.celery_app import celery_app

# Заказ автоматически отменяется если висит в pending больше 30 минут
PENDING_TIMEOUT_MINUTES = 30


@celery_app.task(name="src.worker.tasks.cancel_expired_orders")
def cancel_expired_orders() -> dict:
    """Отменяет заказы со статусом pending старше 30 минут."""
    return asyncio.run(_cancel_expired_orders_async())


async def _cancel_expired_orders_async() -> dict:
    """Async-логика отмены заказов."""
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    threshold = datetime.now(timezone.utc) - timedelta(minutes=PENDING_TIMEOUT_MINUTES)

    try:
        async with session_factory() as db:
            # Находим все просроченные pending-заказы
            query = select(Order).where(
                Order.status == OrderStatus.PENDING,
                Order.created_at < threshold,
            )
            result = await db.execute(query)
            orders = result.scalars().all()

            if not orders:
                return {"cancelled": 0}

            # Отменяем каждый отдельно
            order_ids = [o.id for o in orders]
            await db.execute(
                update(Order)
                .where(Order.id.in_(order_ids))
                .values(status=OrderStatus.CANCELLED)
            )
            await db.commit()

            return {"cancelled": len(order_ids), "order_ids": order_ids}
    finally:
        await engine.dispose()
