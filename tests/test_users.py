"""Тесты для маршрутов пользователей: регистрация, авторизация, чтение, обновление и удаление."""

import pytest

from tests.conftest import register_and_login


@pytest.mark.asyncio
async def test_get_user_by_id_authorized(async_client) -> None:
    """
    Тестирует получение данных другого пользователя по ID при наличии авторизации.
    """
    token1 = await register_and_login(async_client, "user1", "user1@example.com", "1234")
    token2 = await register_and_login(async_client, "user2", "user2@example.com", "1234")

    headers2 = {"Authorization": f"Bearer {token2}"}
    user2_id = (await async_client.get("/users/me", headers=headers2)).json()["id"]

    headers1 = {"Authorization": f"Bearer {token1}"}
    response = await async_client.get(f"/users/{user2_id}", headers=headers1)

    assert response.status_code == 200
    assert response.json()["username"] == "user2"


@pytest.mark.asyncio
async def test_get_user_by_id_unauthorized(async_client) -> None:
    """
    Тестирует отказ в доступе к данным пользователя по ID без авторизации.
    """
    response = await async_client.get("/users/1")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_users_list(async_client) -> None:
    """
    Тестирует получение списка всех пользователей авторизованным пользователем.
    """
    token = await register_and_login(async_client, "listuser", "list@example.com", "1234")
    headers = {"Authorization": f"Bearer {token}"}

    response = await async_client.get("/users", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_update_own_user(async_client) -> None:
    """
    Тестирует успешное обновление данных собственного пользователя.
    """
    token = await register_and_login(async_client, "editme", "editme@example.com", "1234")
    headers = {"Authorization": f"Bearer {token}"}
    user_id = (await async_client.get("/users/me", headers=headers)).json()["id"]

    update_data = {"username": "edited", "email": "new_email@example.com"}
    response = await async_client.put(f"/users/{user_id}", json=update_data, headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["user"]["username"] == "edited"
    assert data["user"]["email"] == "new_email@example.com"


@pytest.mark.asyncio
async def test_update_other_user_forbidden(async_client) -> None:
    """
    Тестирует запрет на обновление данных чужого пользователя (403).
    """
    token1 = await register_and_login(async_client, "user1", "user1@example.com", "1234")
    token2 = await register_and_login(async_client, "user2", "user2@example.com", "1234")

    headers1 = {"Authorization": f"Bearer {token1}"}
    user1_id = (await async_client.get("/users/me", headers=headers1)).json()["id"]

    headers2 = {"Authorization": f"Bearer {token2}"}
    response = await async_client.put(f"/users/{user1_id}", json={"username": "hacked"}, headers=headers2)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_user_conflict(async_client) -> None:
    """
    Тестирует обновление с конфликтом уникальности username/email (409).
    """
    token1 = await register_and_login(async_client, "user1", "user1@example.com", "1234")
    token2 = await register_and_login(async_client, "user2", "user2@example.com", "1234")

    headers2 = {"Authorization": f"Bearer {token2}"}
    user2_id = (await async_client.get("/users/me", headers=headers2)).json()["id"]

    response = await async_client.put(
        f"/users/{user2_id}",
        json={"username": "user1"},
        headers=headers2
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_user_unauthorized(async_client) -> None:
    """
    Тестирует отказ в обновлении пользователя без авторизации (401).
    """
    response = await async_client.put("/users/1", json={"username": "hacked"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_own_user(async_client) -> None:
    """
    Тестирует успешное удаление собственного пользователя.
    """
    token = await register_and_login(async_client, "delme", "delme@example.com", "1234")
    headers = {"Authorization": f"Bearer {token}"}
    user_id = (await async_client.get("/users/me", headers=headers)).json()["id"]

    delete_response = await async_client.delete(f"/users/{user_id}", headers=headers)
    assert delete_response.status_code == 204

    second_response = await async_client.delete(f"/users/{user_id}", headers=headers)
    assert second_response.status_code == 401


@pytest.mark.asyncio
async def test_delete_other_user_forbidden(async_client) -> None:
    """
    Тестирует запрет на удаление другого пользователя (403).
    """
    token1 = await register_and_login(async_client, "user1", "user1@example.com", "1234")
    token2 = await register_and_login(async_client, "user2", "user2@example.com", "1234")

    headers1 = {"Authorization": f"Bearer {token1}"}
    user1_id = (await async_client.get("/users/me", headers=headers1)).json()["id"]

    headers2 = {"Authorization": f"Bearer {token2}"}
    response = await async_client.delete(f"/users/{user1_id}", headers=headers2)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_user_unauthorized(async_client) -> None:
    """
    Тестирует отказ в удалении пользователя без авторизации (401).
    """
    response = await async_client.delete("/users/1")
    assert response.status_code == 401
