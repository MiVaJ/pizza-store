import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.routers.auth import router as auth_router

# Инициализация Sentry для отслеживания ошибок бэкенда
sentry_sdk.init(
    dsn="",
    traces_sample_rate=1.0,
)

app = FastAPI(title="🍕 Pizza Store API (Educational)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "message": "Асинхронный бэкенд запущен"}
