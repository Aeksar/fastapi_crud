from fastapi.testclient import TestClient
from uuid import uuid4
import pytest
import json

from src.settings import GLOBAL_PREFIX
from src.auth.token import ACCESS_TOKEN_NAME, REFRESH_TOKEN_NAME, VERIFICATION_TOKEN_NAME
from tests.conftest import override_get_redis


class TestAuth:
    """Группа тестов для эндпоинтов /auth"""

    BASE_URL = f"{GLOBAL_PREFIX}/auth"
    CREDENTIALS = {
            "username": "User",
            "password": "12345678Qw.",
        }

    def test_success_autheticate(self, test_client: TestClient, test_user):
        response = test_client.post(f"{self.BASE_URL}/login", data=self.CREDENTIALS)
        content = response.json()
        assert response.status_code == 200
        assert ACCESS_TOKEN_NAME in content
        assert REFRESH_TOKEN_NAME in content


    def test_invalid_autorize_data(self, test_client: TestClient):
        data = {
            "username": "somename",
            "password": "bad pwd"
        }

        response = test_client.post(f"{self.BASE_URL}/login", data=data)
        assert response.status_code == 401
        assert "www-authenticate" in response.headers

    def test_refresh_token(self, test_client: TestClient, test_user):
        response = test_client.post(f"{self.BASE_URL}/login", data=self.CREDENTIALS)
        cookies = dict(response.cookies)
        assert response.status_code == 200
        second_response = test_client.post(f"{self.BASE_URL}/refresh", cookies=cookies)
        print(second_response.json())
        assert second_response.status_code == 200
        assert ACCESS_TOKEN_NAME in second_response.json()
        assert ACCESS_TOKEN_NAME in second_response.cookies

    
    async def test_2fa(self, test_client: TestClient, test_user):
        data = {"is_verified": True}
        update_response = test_client.put(f"{GLOBAL_PREFIX}/users/{test_user["id"]}", json=data)
        assert update_response.status_code == 200

        login_response = test_client.post(f"{self.BASE_URL}/login", data=self.CREDENTIALS)
        assert login_response.status_code == 200
        redis = await anext(override_get_redis())
        code = await redis.get(f"2fa:{test_user["email"]}")
        print(code, "GERE")
        response = test_client.post(f"{self.BASE_URL}/2fa", json={"code": code}, headers={"Authenticate": login_response.cookies.get(VERIFICATION_TOKEN_NAME)})
        print(response.json())
        assert response.status_code == 200
        content = response.json()
        assert ACCESS_TOKEN_NAME in content
        assert REFRESH_TOKEN_NAME in content



