from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase
from src.settings import settings, logger


engine = create_async_engine(settings.ASYNC_DATABASE_URL)
async_session_maker = async_sessionmaker(engine)

class Base(DeclarativeBase):
    ...


async def get_async_session() -> AsyncSession:
    try:
        session = async_session_maker()
        return session
    except Exception as e:
        logger.error(f"Error with connect to db: {e}")
        raise
    finally:
        await session.close()