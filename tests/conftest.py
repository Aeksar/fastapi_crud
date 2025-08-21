import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.db.core import Base
from src.api.endpoints.task import get_async_session
from src.settings import settings
from main import app


engine_test = create_async_engine(settings.TEST_ASYNC_DATABASE_URL)
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture()
async def override_get_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        yield session

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  


@pytest_asyncio.fixture(scope="function")
async def test_client(override_get_db):
    async def override_db():
        yield override_get_db
    app.dependency_overrides[get_async_session] = override_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()