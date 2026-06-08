from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.database import async_session
from src.core.init_db import create_initial_admin
from src.routers.auth import router as auth_router
from src.routers.menu import router as menu_router
from src.routers.order import router as order_router

# Инициализация Sentry для отслеживания ошибок бэкенда
sentry_sdk.init(
    dsn="",
    traces_sample_rate=1.0,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код выполняется строго при старте приложения
    async with async_session() as db:
        await create_initial_admin(db)
    yield


app = FastAPI(
    title="🍕 Pizza Store API (Educational)",
    lifespan=lifespan,
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


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "message": "Асинхронный бэкенд запущен"}
