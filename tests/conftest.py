from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from redis.asyncio.client import Redis
from pathlib import Path
import shutil
import pytest_asyncio
import asyncio
import pytest
import json
import os

from src.db import Base
from src.api.endpoints.task import get_async_session, get_redis
from src.settings.environment import settings, GLOBAL_PREFIX, BASE_DIR
from src.api.endpoints.auth import send_verification_code_task, send_verification_link_task
from src.mailing.verification import send_verification_link, send_verification_code
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
    redis = Redis(
            username=settings.REDIS_USERNAME,
            password=settings.REDIS_PASSWORD,            
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.TEST_REDIS_DB,
            decode_responses=True
        ) 
    yield redis


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
def auth_client(test_user, test_client: TestClient):
    data = {
            "username": "User",
            "password": "12345678Qw.",
        }
    response = test_client.post(f"{GLOBAL_PREFIX}/auth/login", data=data)
    cookies = dict(response.cookies)
    app.dependency_overrides[get_async_session] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis
    for k, v in cookies.items():
        test_client.cookies.set(k, v)
    
    yield test_client


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


@pytest.fixture(autouse=True, scope="session")
def fake_certs():
    certs_dir = BASE_DIR / "certs"
    if not certs_dir.exists():
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

    # monkeypatch.setattr(settings.auth, "public_key", public_path)
    # monkeypatch.setattr(settings.auth, "private_key", private_path)
    yield



@pytest.fixture(autouse=True)
def use_direct_email_sending(monkeypatch):    
    from src.tasks import mailing
    from src.mailing.verification import send_verification_link, send_verification_code
    
    monkeypatch.setattr('src.api.endpoints.auth.send_verification_code_task.kiq', send_verification_code)
    monkeypatch.setattr('src.api.endpoints.auth.send_verification_link_task.kiq', send_verification_link)
    yield