from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.repositories.base.abc import BaseTaskRepository
from src.repositories.base.crud import CrudRepository
from src.api.models.task import TaskResponse
from src.db import Task, get_async_session
from src.utils.redis import Redis, get_redis


__all__ = ["TaskRepository", "BaseTaskRepository", "get_task_repo"]


class TaskRepository(CrudRepository, BaseTaskRepository):
    model = Task
    response_model = TaskResponse


def get_task_repo(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        redis: Annotated[Redis, Depends(get_redis)],
    ) -> BaseTaskRepository:
    return TaskRepository(session, redis)
