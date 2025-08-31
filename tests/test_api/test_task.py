from fastapi.testclient import TestClient
from uuid import uuid4
import pytest
import json

from src.settings import GLOBAL_PREFIX


class TestTaskAPI:
    """Группа тестов для эндпоинтов /tasks"""

    BASE_URL = f"{GLOBAL_PREFIX}/tasks/"
    
    def test_create_task_success(self, test_client: TestClient, test_user: dict):
        """Тест успешного создания задачи."""
        data = {"name": "Test Task", "description": "some descrip", "owner_id": test_user["id"]}
        response = test_client.post(self.BASE_URL, json=data)

        assert response.status_code == 201
        response_json = response.json()
        assert response_json["name"] == data["name"]
        assert response_json["description"] == data["description"]
        assert "id" in response_json
        assert response_json["status"] == "создано"

    def test_create_task_validation_error(self, test_client: TestClient):
        """Тест ошибки валидации при создании задачи (отсутствует обязательное поле name)."""
        task_data = {"description": "Missing name"}
        response = test_client.post(self.BASE_URL, json=json.dumps(task_data))

        assert response.status_code == 422

    def test_get_task_not_found(self, test_client: TestClient):
        """Тест получения несуществующей задачи."""
        random_uuid = uuid4()
        response = test_client.get(f"{self.BASE_URL}{random_uuid}")
        assert response.status_code == 404

    def test_get_task_success(self, test_client: TestClient, test_task: dict):
        """Тест успешного получения одной задачи."""
        get_response = test_client.get(f"{self.BASE_URL}{test_task["id"]}")
        assert get_response.status_code == 200
        get_task_json = get_response.json()
        assert get_task_json["id"] == test_task["id"]
        assert get_task_json["name"] == test_task["name"]

    def test_get_tasks_empty_list(self, test_client: TestClient):
        """Тест получения пустого списка задач."""
        response = test_client.get(self.BASE_URL)
        assert response.status_code == 200
        assert response.json() == []

    def test_get_tasks_list_and_filter(self, test_client: TestClient, test_user: dict):
        """Тест получения списка задач, пагинации и фильтрации."""
        test_client.post(self.BASE_URL, json={"name": "Task A", "owner_id": test_user["id"]})
        test_client.post(self.BASE_URL, json={"name": "Task B", "status": "в работе", "owner_id": test_user["id"]})
        test_client.post(self.BASE_URL, json={"name": "Task C", "status": "в работе", "owner_id": test_user["id"]})
        test_client.post(self.BASE_URL, json={"name": "Task D", "status": "завершено", "owner_id": test_user["id"]})

        response_all =  test_client.get(self.BASE_URL)
        assert response_all.status_code == 200
        assert len(response_all.json()) == 4

        response_filtered =  test_client.get(self.BASE_URL, params={"status": "в работе"})
        assert response_filtered.status_code == 200
        filtered_data = response_filtered.json()
        assert len(filtered_data) == 2
        assert filtered_data[0]["name"] == "Task B"
        assert filtered_data[1]["name"] == "Task C"

        response_limit =  test_client.get(self.BASE_URL, params={"limit": 1})
        assert response_limit.status_code == 200
        assert len(response_limit.json()) == 1

        response_skip =  test_client.get(self.BASE_URL, params={"skip": 2, "limit": 2})
        assert response_skip.status_code == 200
        skip_data = response_skip.json()
        assert len(skip_data) == 2
        assert skip_data[0]["name"] == "Task C"

    def test_update_task_success(self, test_client: TestClient, test_task: dict):
        """Тест успешного обновления задачи."""
        task_id = test_task["id"]

        update_data = {"name": "Updated Name", "status": "завершено"}
        update_response =  test_client.put(f"{self.BASE_URL}{task_id}", json=update_data)
        
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["id"] == task_id
        assert updated_task["name"] == update_data["name"]
        assert updated_task["status"] == update_data["status"]

    def test_update_task_not_found(self, test_client: TestClient):
        """Тест обновления несуществующей задачи."""
        random_uuid = uuid4()
        update_data = {"name": "Won't be updated"}
        response = test_client.put(f"{self.BASE_URL}{random_uuid}", json=update_data)
        assert response.status_code == 404

    def test_delete_task_success(self, test_client: TestClient, test_task: dict):
        """Тест успешного удаления задачи."""
        task_id = test_task["id"]

        delete_response = test_client.delete(f"{self.BASE_URL}{task_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["id"] == task_id

        get_response = test_client.get(f"{self.BASE_URL}{task_id}")
        assert get_response.status_code == 404

    def test_delete_task_not_found(self, test_client: TestClient):
        """Тест удаления несуществующей задачи."""
        random_uuid = uuid4()
        response =  test_client.delete(f"{self.BASE_URL}{random_uuid}")
        assert response.status_code == 404