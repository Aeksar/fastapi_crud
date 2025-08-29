from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from typing import Annotated, Optional
from uuid import UUID

from src.repositories import BaseTaskRepository, TaskRepository
from src.api.models.task import TaskCreate, TaskResponse, TaskUpdate
from src.utils.enums import TaskStatusEnum
from src.utils.redis import get_redis
from src.db.core import get_async_session


task_router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_task_repo(
        session: Annotated[AsyncSession, Depends(get_async_session)],
        redis: Annotated[Redis, Depends(get_redis)],
    ) -> BaseTaskRepository:
    return TaskRepository(session, redis)


@task_router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    repo: Annotated[BaseTaskRepository, Depends(get_task_repo)],
    skip: Optional[int] = 0,
    limit: Optional[int] = 50,
    status: Optional[TaskStatusEnum] = None,
):
    """Возвращает лист задач с возможностью пагинации и фильтрации по статусу"""
    return await repo.get_list(skip, limit, status=status)


@task_router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: TaskCreate,
    repo: Annotated[BaseTaskRepository, Depends(get_task_repo)],
):
    """Создает новую задачу"""
    return await repo.create(task)


@task_router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    repo: Annotated[BaseTaskRepository, Depends(get_task_repo)],
):
    """Возвращает одну задачу"""
    return await repo.get(task_id)


@task_router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    repo: Annotated[BaseTaskRepository, Depends(get_task_repo)],
):
    """Обновляет задачу"""
    return await repo.update(task_id, task_update)


@task_router.delete("/{task_id}", response_model=TaskResponse)
async def delete_task(
    task_id: UUID,
    repo: Annotated[BaseTaskRepository, Depends(get_task_repo)],
):
    """Удаляет задачу"""
    return await repo.delete(task_id)
