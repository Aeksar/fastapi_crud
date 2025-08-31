from fastapi.testclient import TestClient
from uuid import uuid4
import pytest
import json

from src.settings import GLOBAL_PREFIX, logger


class TestUserAPI:
    """Группа тестов для эндпоинтов /users"""

    BASE_URL = f"{GLOBAL_PREFIX}/users/"
    
    def test_create_user_success(self, test_client: TestClient):
        """Тест успешного создания пользователя."""
        data = {
            "name": "User",
            "surname": "Test",
            "email": "user@example.com",
            "birthdate": "2025-08-08",
            "password": "12345678Qw."
        }
        response = test_client.post(self.BASE_URL, json=data)

        assert response.status_code == 201
        response_json = response.json()
        assert response_json["name"] == data["name"]
        assert response_json["surname"] == data["surname"]
        assert "id" in response_json and "role" in response_json and "hashed_password" in response_json
        assert response_json["role"] == "Пользователь"

    def test_create_user_not_uinique_email(self, test_client: TestClient, test_user: dict):
        """Тест не уникального email при создании пользователя."""
        data = {
            "name": "User",
            "surname": "Test",
            "email": "user@example.com",
            "birthdate": "2025-08-08",
            "password": "12345678Qw."
        }
        response = test_client.post(self.BASE_URL, json=data)

        assert response.status_code == 400

    def test_create_user_validation_error(self, test_client: TestClient):
        """Тест ошибки валидации при создании пользователя (не прваильный пароль)."""
        data = {
            "name": "User",
            "surname": "Test",
            "email": "user@example.com",
            "birthdate": "2025-08-08",
            "password": "wrong pwd"
        }
        response = test_client.post(self.BASE_URL, json=json.dumps(data))
        logger.error(response.json())
        assert response.status_code == 422
        

    def test_get_user_not_found(self, test_client: TestClient):
        """Тест получения несуществующего пользователя."""
        random_uuid = uuid4()
        response = test_client.get(f"{self.BASE_URL}{random_uuid}")
        assert response.status_code == 404

    def test_get_user_success(self, test_client: TestClient, test_user: dict):
        """Тест успешного получения одного пользователя."""
        get_response = test_client.get(f"{self.BASE_URL}{test_user["id"]}")
        assert get_response.status_code == 200
        get_user_json = get_response.json()
        assert get_user_json["id"] == test_user["id"]
        assert get_user_json["name"] == test_user["name"]

    def test_get_users_empty_list(self, test_client: TestClient):
        """Тест получения пустого списка пользователей."""
        response = test_client.get(self.BASE_URL)
        assert response.status_code == 200
        assert response.json() == []

    def test_update_user_success(self, test_client: TestClient, test_user: dict):
        """Тест успешного обновления пользователя."""
        user_id = test_user["id"]

        update_data = {"name": "Updated Name", "role": "Администратор"}
        update_response =  test_client.put(f"{self.BASE_URL}{user_id}", json=update_data)
        
        assert update_response.status_code == 200
        updated_user = update_response.json()
        assert updated_user["id"] == user_id
        assert updated_user["name"] == update_data["name"]
        assert updated_user["role"] == update_data["role"]

    def test_update_user_not_found(self, test_client: TestClient):
        """Тест обновления несуществующего пользователя."""
        random_uuid = uuid4()
        update_data = {"name": "Won't be updated"}
        response = test_client.put(f"{self.BASE_URL}{random_uuid}", json=update_data)
        assert response.status_code == 404

    def test_delete_user_success(self, test_client: TestClient, test_user: dict):
        """Тест успешного удаления пользователя."""
        user_id = test_user["id"]

        delete_response = test_client.delete(f"{self.BASE_URL}{user_id}")
        assert delete_response.status_code == 200
        assert delete_response.json()["id"] == user_id

        get_response = test_client.get(f"{self.BASE_URL}{user_id}")
        assert get_response.status_code == 404

    def test_delete_user_not_found(self, test_client: TestClient):
        """Тест удаления несуществующего пользователя."""
        random_uuid = uuid4()
        response =  test_client.delete(f"{self.BASE_URL}{random_uuid}")
        assert response.status_code == 404