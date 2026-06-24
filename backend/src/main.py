import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.payments.router import router as payments_router
from src.routers.auth import router as auth_router
from src.routers.menu import router as menu_router
from src.routers.order import router as order_router

# Инициализация Sentry для отслеживания ошибок бэкенда
sentry_sdk.init(
    dsn="",
    traces_sample_rate=1.0,
)


app = FastAPI(
    title="🍕 Pizza Store API (Educational)",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(menu_router)
app.include_router(order_router)
app.include_router(payments_router)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "message": "Асинхронный бэкенд запущен"}
