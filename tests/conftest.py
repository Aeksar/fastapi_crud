from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from pathlib import Path
import requests
import shutil
import pytest_asyncio
import pytest
import json
import os

from src.db import Base
from src.api.endpoints.task import get_async_session, get_redis
from src.settings.environment import settings, GLOBAL_PREFIX, BASE_DIR
from main import app


async def override_get_db():
    engine_test = create_async_engine(settings.TEST_ASYNC_DATABASE_URL)
    async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False, autoflush=False)

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        yield session


REDIS_DATA = {}
async def override_get_redis():
    class MockRedis():
        def __init__(self):
            self.storage = REDIS_DATA

        async def get(self, key, *args, **kwargs):
            return self.storage.get(key)
        
        async def set(self, key, val, *args, **kwargs):
            self.storage[key] = val

        async def delete(self, key, *args, **kwargs):
            self.storage.pop(key)

    yield MockRedis()


@pytest.fixture(scope="function", autouse=True)
def test_db_session():
    engine = create_engine(settings.TEST_DATABASE_URL) 
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def test_client():
    app.dependency_overrides[get_async_session] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_client(test_user):
    data = {
            "username": "User",
            "password": "12345678Qw.",
        }
    response = requests.post(f"http://localhost:8000/{GLOBAL_PREFIX}/auth/login", data=data)
    cookies = dict(response.cookies)
    app.dependency_overrides[get_async_session] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    with TestClient(app, cookies=cookies) as c:
        yield c


@pytest_asyncio.fixture
async def test_user(test_client: TestClient):
    data = {
        "name": "User",
        "surname": "Test",
        "email": "user@example.com",
        "birthdate": "2025-08-08",
        "password": "12345678Qw."
    }
    yield test_client.post(f"{GLOBAL_PREFIX}/users/", json=data).json()


@pytest.fixture
def test_task(test_client: TestClient, test_user: dict):
    data = {"name": "test task", "description": "test task description", "owner_id": test_user["id"]}
    yield test_client.post(f"{GLOBAL_PREFIX}/tasks", content=json.dumps(data)).json()


@pytest.fixture(autouse=True)
def fake_certs(monkeypatch):
    certs_dir = BASE_DIR / "certs"
    certs_dir.mkdir(exist_ok=True)

    private_path =  BASE_DIR / "certs" / "private.pem"
    public_path =  BASE_DIR / "certs" / "public.pem"

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    
    private_path.write_bytes(private_pem)
    public_path.write_bytes(public_pem)

    monkeypatch.setattr(settings.auth, "public_key", public_path)
    monkeypatch.setattr(settings.auth, "private_key", private_path)
    
    yield

    shutil.rmtree(certs_dir, ignore_errors=True)