"""Тесты для маршрутов пользователей: регистрация, логин, получение текущего пользователя и валидация ошибок."""

import pytest

from tests.conftest import register_and_login


@pytest.mark.asyncio
async def test_register_and_login(async_client) -> None:
    """
    Проверка успешной регистрации и получения токена.
    """
    token = await register_and_login(
        async_client,
        username="testuser",
        email="testuser@example.com",
        password="1234"
    )
    assert token


@pytest.mark.asyncio
async def test_get_current_user(async_client) -> None:
    """
    Проверка получения текущего пользователя по валидному токену.
    """
    token = await register_and_login(
        async_client,
        username="meuser",
        email="meuser@example.com",
        password="1234"
    )

    me_response = await async_client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["username"] == "meuser"
    assert me_data["email"] == "meuser@example.com"


@pytest.mark.asyncio
async def test_register_existing_user(async_client) -> None:
    """
    Проверка ошибки при регистрации с уже существующими username/email.
    """
    await register_and_login(
        async_client,
        username="duplicate",
        email="duplicate@example.com",
        password="1234"
    )
    response = await async_client.post("/users/register", json={
        "username": "duplicate",
        "email": "duplicate@example.com",
        "password": "1234"
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_invalid_password(async_client) -> None:
    """
    Проверка ошибки при вводе неверного пароля.
    """
    await register_and_login(
        async_client,
        username="wrongpass",
        email="wrongpass@example.com",
        password="OK_password"
    )
    response = await async_client.post("/users/login", data={
        "username": "wrongpass",
        "password": "BAD_password"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_invalid_username(async_client) -> None:
    """
    Проверка ошибки при вводе несуществующего имени пользователя.
    """
    await register_and_login(
        async_client,
        username="correctname",
        email="wrongpass@example.com",
        password="OK_password"
    )
    response = await async_client.post("/users/login", data={
        "username": "wrongname",
        "password": "OK_password"
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(async_client):
    # Регистрация и логин
    register_response = await async_client.post("/users/register", json={
        "username": "refresher",
        "email": "refresher@example.com",
        "password": "1234"
    })
    assert register_response.status_code == 201

    login_response = await async_client.post("/users/login", data={
        "username": "refresher",
        "password": "1234"
    })
    assert login_response.status_code == 200

    tokens = login_response.json()
    assert "refresh_token" in tokens
    old_access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # Обновление токена
    refresh_response = await async_client.post("/users/refresh", json={
        "refresh_token": refresh_token
    })
    assert refresh_response.status_code == 200

    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
    assert new_tokens["access_token"] != old_access_token
    assert new_tokens["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_me_without_token(async_client) -> None:
    """
    Проверка запроса к /users/me без токена (должен вернуть 401).
    """
    response = await async_client.get("/users/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_invalid_token(async_client) -> None:
    """
    Проверка запроса к /users/me с некорректным токеном (должен вернуть 401).
    """
    response = await async_client.get("/users/me", headers={
        "Authorization": "Bearer invalidtoken"
    })
    assert response.status_code == 401
