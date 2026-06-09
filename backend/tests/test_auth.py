import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    """Регистрация нового пользователя."""
    response = await client.post(
        "/api/auth/register",
        json={
            "email": "test@pizza.ru",
            "password": "secret123",
            "name": "Тестовый пользователь",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@pizza.ru"
    assert data["name"] == "Тестовый пользователь"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    """Нельзя зарегистрировать два аккаунта с одним email."""
    payload = {"email": "dupe@pizza.ru", "password": "secret123"}
    await client.post("/api/auth/register", json=payload)
    response = await client.post("/api/auth/register", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_success(client):
    """Успешный вход возвращает 200 и устанавливает куки."""
    await client.post(
        "/api/auth/register",
        json={
            "email": "login@pizza.ru",
            "password": "secret123",
        },
    )
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "login@pizza.ru",
            "password": "secret123",
        },
    )
    assert response.status_code == 200
    assert "fastapi_access" in response.cookies


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """Неверный пароль возвращает 401."""
    await client.post(
        "/api/auth/register",
        json={
            "email": "wrong@pizza.ru",
            "password": "secret123",
        },
    )
    response = await client.post(
        "/api/auth/login",
        json={
            "email": "wrong@pizza.ru",
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client):
    """GET /auth/me возвращает данные авторизованного пользователя."""
    await client.post(
        "/api/auth/register",
        json={
            "email": "me@pizza.ru",
            "password": "secret123",
            "name": "Я",
        },
    )
    await client.post(
        "/api/auth/login",
        json={
            "email": "me@pizza.ru",
            "password": "secret123",
        },
    )
    response = await client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == "me@pizza.ru"


@pytest.mark.asyncio
async def test_get_me_unauthorized(client):
    """GET /auth/me без авторизации возвращает 401."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401
