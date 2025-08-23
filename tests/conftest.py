from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine
from redis.asyncio.client import Redis
from unittest.mock import AsyncMock
import pytest
import json

from src.db import Base
from src.api.endpoints.task import get_async_session, get_redis
from src.settings.environment import settings
from main import app


async def override_get_db():
    engine_test = create_async_engine(settings.TEST_ASYNC_DATABASE_URL)
    async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False, autoflush=False)

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        yield session


async def override_get_redis():
    redis_mock = AsyncMock(spec=Redis)

    async def mock_get(key, *args, **kwargs):
        return None
    
    async def mock_set(key, value, ex, *args, **kwargs):
        pass

    redis_mock.get.side_effect = mock_get
    redis_mock.set.side_effect = mock_set
    yield redis_mock


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



