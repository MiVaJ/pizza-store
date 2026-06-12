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


@pytest.mark.asyncio
async def test_patch_me_success(client):
    """Успешное обновление имени и телефона."""
    await client.post(
        "/api/auth/register",
        json={
            "email": "patch@pizza.ru",
            "password": "secret123",
            "name": "Старое имя",
        },
    )
    await client.post(
        "/api/auth/login",
        json={
            "email": "patch@pizza.ru",
            "password": "secret123",
        },
    )

    response = await client.patch(
        "/api/auth/me",
        json={
            "name": "Новое имя",
            "phone": "9001234567",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Новое имя"
    assert data["phone"] == "9001234567"


@pytest.mark.asyncio
async def test_patch_me_partial(client):
    """Можно обновить только одно поле — второе остаётся без изменений."""
    await client.post(
        "/api/auth/register",
        json={
            "email": "partial@pizza.ru",
            "password": "secret123",
            "name": "Исходное имя",
            "phone": "9009999999",
        },
    )
    await client.post(
        "/api/auth/login",
        json={
            "email": "partial@pizza.ru",
            "password": "secret123",
        },
    )

    response = await client.patch("/api/auth/me", json={"name": "Новое имя"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Новое имя"
    assert data["phone"] == "9009999999"  # телефон не тронут


@pytest.mark.asyncio
async def test_patch_me_phone_taken(client):
    """Нельзя взять телефон который уже занят другим пользователем."""
    await client.post(
        "/api/auth/register",
        json={
            "email": "owner@pizza.ru",
            "password": "secret123",
            "phone": "9001111111",
        },
    )
    await client.post(
        "/api/auth/register",
        json={
            "email": "thief@pizza.ru",
            "password": "secret123",
        },
    )
    await client.post(
        "/api/auth/login",
        json={
            "email": "thief@pizza.ru",
            "password": "secret123",
        },
    )

    response = await client.patch("/api/auth/me", json={"phone": "9001111111"})
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_patch_me_unauthorized(client):
    """Обновление профиля без авторизации возвращает 401."""
    response = await client.patch("/api/auth/me", json={"name": "Хакер"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_patch_me_invalid_phone(client):
    """Телефон короче 10 цифр не проходит валидацию."""
    await client.post(
        "/api/auth/register",
        json={
            "email": "phone@pizza.ru",
            "password": "secret123",
        },
    )
    await client.post(
        "/api/auth/login",
        json={
            "email": "phone@pizza.ru",
            "password": "secret123",
        },
    )

    response = await client.patch("/api/auth/me", json={"phone": "123"})
    assert response.status_code == 422
