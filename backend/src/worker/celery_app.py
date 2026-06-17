from celery import Celery

from src.core.config import settings

celery_app = Celery(
    "pizza_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Расписание задач
    beat_schedule={
        "cancel-pending-orders-every-minute": {
            "task": "src.worker.tasks.cancel_expired_orders",
            "schedule": 60.0,  # Каждую минуту
        },
    },
)
