import pytest
from uuid import uuid4
from httpx import AsyncClient
import json

BASE_URL = "/api/v1/tasks/"

@pytest.mark.asyncio
class TestTaskAPI:
    """Группа тестов для эндпоинтов /tasks/."""

    async def test_create_task_success(self, test_client: AsyncClient):
        """Тест успешного создания задачи."""
        task_data = {"name": "Test Task 1", "description": "Description for task 1"}
        response = await test_client.post(BASE_URL, content=json.dumps(task_data))

        assert response.status_code == 201
        response_json = response.json()
        assert response_json["name"] == task_data["name"]
        assert response_json["description"] == task_data["description"]
        assert "id" in response_json
        assert response_json["status"] == "создано"

    async def test_create_task_validation_error(self, test_client: AsyncClient):
        """Тест ошибки валидации при создании задачи (отсутствует обязательное поле name)."""
        task_data = {"description": "Missing name"}
        response = await test_client.post(BASE_URL, json=json.dumps(task_data))

        assert response.status_code == 422

    async def test_get_task_not_found(self, test_client: AsyncClient):
        """Тест получения несуществующей задачи."""
        random_uuid = uuid4()
        response = await test_client.get(f"{BASE_URL}{random_uuid}")
        assert response.status_code == 404

    async def test_get_task_success(self, test_client: AsyncClient):
        """Тест успешного получения одной задачи."""
        # Сначала создаем задачу
        task_data = {"name": "Task to get", "description": "Get me!"}
        create_response = await test_client.post(BASE_URL, content=json.dumps(task_data))
        assert create_response.status_code == 201
        created_task_id = create_response.json()["id"]

        # Затем получаем её
        get_response = await test_client.get(f"{BASE_URL}{created_task_id}")
        assert get_response.status_code == 200
        get_task_json = get_response.json()
        assert get_task_json["id"] == created_task_id
        assert get_task_json["name"] == task_data["name"]

    async def test_get_tasks_empty_list(self, test_client: AsyncClient):
        """Тест получения пустого списка задач."""
        response = await test_client.get(BASE_URL)
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_tasks_list_and_filter(self, test_client: AsyncClient):
        """Тест получения списка задач, пагинации и фильтрации."""
        # Создаем несколько задач
        await test_client.post(BASE_URL, json={"name": "Task A", "status": "todo"})
        await test_client.post(BASE_URL, json={"name": "Task B", "status": "in_progress"})
        await test_client.post(BASE_URL, json={"name": "Task C", "status": "in_progress"})
        await test_client.post(BASE_URL, json={"name": "Task D", "status": "done"})

        # 1. Получаем полный список
        response_all = await test_client.get(BASE_URL)
        assert response_all.status_code == 200
        assert len(response_all.json()) == 4

        # 2. Фильтруем по статусу 'in_progress'
        response_filtered = await test_client.get(BASE_URL, params={"status": "in_progress"})
        assert response_filtered.status_code == 200
        filtered_data = response_filtered.json()
        assert len(filtered_data) == 2
        assert filtered_data[0]["name"] == "Task B"
        assert filtered_data[1]["name"] == "Task C"

        # 3. Проверяем пагинацию (limit)
        response_limit = await test_client.get(BASE_URL, params={"limit": 1})
        assert response_limit.status_code == 200
        assert len(response_limit.json()) == 1

        # 4. Проверяем пагинацию (skip)
        response_skip = await test_client.get(BASE_URL, params={"skip": 2, "limit": 2})
        assert response_skip.status_code == 200
        skip_data = response_skip.json()
        assert len(skip_data) == 2
        assert skip_data[0]["name"] == "Task C"

    async def test_update_task_success(self, test_client: AsyncClient):
        """Тест успешного обновления задачи."""
        # Создаем задачу
        create_response = await test_client.post(BASE_URL, json={"name": "Original Name"})
        created_task = create_response.json()
        task_id = created_task["id"]

        # Обновляем её
        update_data = {"name": "Updated Name", "status": "done"}
        update_response = await test_client.put(f"{BASE_URL}{task_id}", json=update_data)
        
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["id"] == task_id
        assert updated_task["name"] == update_data["name"]
        assert updated_task["status"] == update_data["status"]

    async def test_update_task_not_found(self, test_client: AsyncClient):
        """Тест обновления несуществующей задачи."""
        random_uuid = uuid4()
        update_data = {"name": "Won't be updated"}
        response = await test_client.put(f"{BASE_URL}{random_uuid}", json=update_data)
        assert response.status_code == 404

    async def test_delete_task_success(self, test_client: AsyncClient):
        """Тест успешного удаления задачи."""
        # Создаем задачу
        create_response = await test_client.post(BASE_URL, json={"name": "To be deleted"})
        task_id = create_response.json()["id"]

        # Удаляем её
        delete_response = await test_client.delete(f"{BASE_URL}{task_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["id"] == task_id # Эндпоинт возвращает удаленный объект

        # Проверяем, что она действительно удалена
        get_response = await test_client.get(f"{BASE_URL}{task_id}")
        assert get_response.status_code == 404

    async def test_delete_task_not_found(self, test_client: AsyncClient):
        """Тест удаления несуществующей задачи."""
        random_uuid = uuid4()
        response = await test_client.delete(f"{BASE_URL}{random_uuid}")
        assert response.status_code == 404