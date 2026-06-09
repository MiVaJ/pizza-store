import pytest


async def register_and_login(client, email="order@pizza.ru"):
    """Вспомогательная функция — регистрация и вход."""
    await client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "secret123",
        },
    )
    await client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": "secret123",
        },
    )


@pytest.mark.asyncio
async def test_get_my_orders_empty(client):
    """История заказов пустая у нового пользователя."""
    await register_and_login(client)
    response = await client.get("/api/orders/my")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_my_orders_unauthorized(client):
    """История заказов недоступна без авторизации."""
    response = await client.get("/api/orders/my")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_my_stats_empty(client):
    """Статистика у нового пользователя возвращает нули."""
    await register_and_login(client)
    response = await client.get("/api/orders/my/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_orders"] == 0
    assert data["total_spent"] == 0
    assert data["favourite_pizza"] is None
