from .task import TaskRepository
from .base.abc import BaseTaskRepository


from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from typing import Annotated

from src.db.core import get_async_session


def get_task_repo(session: Annotated[AsyncSession, Depends(get_async_session)]) -> BaseTaskRepository:
    return TaskRepository(session)