"""Тесты для маршрутов задач: создание, получение, обновление и удаление."""

import pytest

from tests.conftest import register_and_login


@pytest.mark.asyncio
async def test_create_task_success(async_client) -> None:
    """
    Проверка успешного создания задачи авторизованным пользователем.
    """
    token = await register_and_login(async_client, "taskuser", "task@example.com", "1234")
    headers = {"Authorization": f"Bearer {token}"}
    task_data = {"title": "Test Task", "description": "Test Description", "status": "IN_PROGRESS"}

    response = await async_client.post("/tasks", json=task_data, headers=headers)
    assert response.status_code == 201

    data = response.json()
    assert data["title"] == "Test Task"
    assert data["description"] == "Test Description"
    assert data["status"] == "IN_PROGRESS"
    assert "id" in data
    assert "user_id" in data


@pytest.mark.asyncio
async def test_create_task_unauthorized(async_client) -> None:
    """
    Проверка ошибки создания задачи без авторизации.
    """
    task_data = {"title": "Test Task", "description": "Test Description", "status": "IN_PROGRESS"}
    response = await async_client.post("/tasks", json=task_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_all_tasks_only_own(async_client) -> None:
    """
    Проверка получения только своих задач.
    """
    token1 = await register_and_login(async_client, "user1", "user1@example.com", "1234")
    token2 = await register_and_login(async_client, "user2", "user2@example.com", "1234")
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    await async_client.post("/tasks", json={"title": "first_user_task"}, headers=headers1)
    await async_client.post("/tasks", json={"title": "first_user_task"}, headers=headers1)
    await async_client.post("/tasks", json={"title": "second_user_task"}, headers=headers2)

    me_response = await async_client.get("/users/me", headers=headers1)
    user1_id = me_response.json()["id"]

    response = await async_client.get("/tasks", headers=headers1)
    assert response.status_code == 200
    tasks = response.json()

    assert len(tasks) == 2
    for task in tasks:
        assert task["user_id"] == user1_id
        assert task["title"].startswith("first")


@pytest.mark.asyncio
async def test_get_task_by_id_success(async_client) -> None:
    """
    Проверка успешного получения задачи по ID.
    """
    token = await register_and_login(async_client, "taskreader", "reader@example.com", "1234")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await async_client.post("/tasks", json={"title": "pass"}, headers=headers)
    task_id = create_resp.json()["id"]

    get_resp = await async_client.get(f"/tasks/{task_id}", headers=headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == task_id


@pytest.mark.asyncio
async def test_get_task_forbidden(async_client) -> None:
    """
    Проверка запрета на просмотр чужой задачи.
    """
    token1 = await register_and_login(async_client, "owner", "owner@example.com", "1234")
    token2 = await register_and_login(async_client, "stranger", "stranger@example.com", "1234")
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    resp = await async_client.post("/tasks", json={"title": "private task"}, headers=headers1)
    task_id = resp.json()["id"]

    forbidden = await async_client.get(f"/tasks/{task_id}", headers=headers2)
    assert forbidden.status_code == 403


@pytest.mark.asyncio
async def test_get_task_not_found(async_client) -> None:
    """
    Проверка ошибки при запросе несуществующей задачи.
    """
    token = await register_and_login(async_client, "taskreader", "reader@example.com", "1234")
    headers = {"Authorization": f"Bearer {token}"}
    resp = await async_client.get("/tasks/9999", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_own_task(async_client) -> None:
    """
    Проверка успешного обновления своей задачи.
    """
    token = await register_and_login(async_client, "taskreader", "reader@example.com", "1234")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await async_client.post("/tasks", json={"title": "old_task"}, headers=headers)
    task_id = create_resp.json()["id"]

    update_data = {
        "title": "new_task",
        "description": "super_new_task",
        "status": "COMPLETED"
    }
    update_resp = await async_client.put(f"/tasks/{task_id}", json=update_data, headers=headers)
    assert update_resp.status_code == 200

    data = update_resp.json()
    assert data["title"] == "new_task"
    assert data["description"] == "super_new_task"
    assert data["status"] == "COMPLETED"


@pytest.mark.asyncio
async def test_update_other_task_forbidden(async_client) -> None:
    """
    Проверка запрета на обновление чужой задачи.
    """
    token1 = await register_and_login(async_client, "owner", "owner@example.com", "1234")
    token2 = await register_and_login(async_client, "intruder", "intruder@example.com", "1234")
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    create_resp = await async_client.post("/tasks", json={"title": "Secret"}, headers=headers1)
    task_id = create_resp.json()["id"]

    forbidden = await async_client.put(f"/tasks/{task_id}", json={"title": "Hacked"}, headers=headers2)
    assert forbidden.status_code == 403


@pytest.mark.asyncio
async def test_update_task_not_found(async_client) -> None:
    """
    Проверка обновления несуществующей задачи.
    """
    token = await register_and_login(async_client, "ghost", "ghost@example.com", "1234")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await async_client.put("/tasks/9999", json={"title": "Nothing"}, headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_own_task(async_client) -> None:
    """
    Проверка успешного удаления своей задачи.
    """
    token = await register_and_login(async_client, "deleter", "deleter@example.com", "1234")
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await async_client.post("/tasks", json={"title": "To delete"}, headers=headers)
    task_id = create_resp.json()["id"]

    delete_resp = await async_client.delete(f"/tasks/{task_id}", headers=headers)
    assert delete_resp.status_code == 204

    second_delete = await async_client.delete(f"/tasks/{task_id}", headers=headers)
    assert second_delete.status_code == 404


@pytest.mark.asyncio
async def test_delete_other_task_forbidden(async_client) -> None:
    """
    Проверка запрета на удаление чужой задачи.
    """
    token1 = await register_and_login(async_client, "owner", "owner@example.com", "1234")
    token2 = await register_and_login(async_client, "attacker", "attacker@example.com", "1234")
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    create_resp = await async_client.post("/tasks", json={"title": "Do not touch"}, headers=headers1)
    task_id = create_resp.json()["id"]

    resp = await async_client.delete(f"/tasks/{task_id}", headers=headers2)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_delete_task_not_found(async_client) -> None:
    """
    Проверка удаления несуществующей задачи.
    """
    token = await register_and_login(async_client, "ghost", "ghost@example.com", "1234")
    headers = {"Authorization": f"Bearer {token}"}

    resp = await async_client.delete("/tasks/9999", headers=headers)
    assert resp.status_code == 404
