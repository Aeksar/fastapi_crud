from fastapi import APIRouter, Depends, status
from typing import Annotated, Optional
from uuid import UUID

from src.repositories.abc import BaseTaskRepository
from src.repositories.task import TaskRepository
from src.api.models.task import TaskCreate, TaskResponse, TaskUpdate
from src.utils.enums import TaskStatusEnum
from src.db.core import get_async_session, AsyncSession


task_router = APIRouter(prefix="/tasks", tags=["Tasks"])

def get_task_repo(session: Annotated[AsyncSession, Depends(get_async_session)]) -> TaskRepository:
    return TaskRepository(session)


@task_router.get("/", response_model=list[TaskResponse])
async def get_tasks(
    repo: Annotated[BaseTaskRepository, Depends(get_task_repo)],
    skip: Optional[int] = 0,
    limit: Optional[int] = 50,
    status: Optional[TaskStatusEnum] = None,
):
    """Возвращает лист задач с возможностью пагинации и фильтрации по статусу"""
    return await repo.get_list(skip, limit, status)


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
