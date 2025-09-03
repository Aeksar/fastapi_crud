from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from redis import Redis
from typing import Annotated, Optional
from uuid import UUID

from src.repositories import BaseTaskRepository, TaskRepository, UserService
from src.repositories.user import get_user_repo
from src.repositories.task import get_task_repo
from src.api.models.task import TaskCreate, TaskResponse, TaskUpdate
from src.api.models.user import UserResponse
from src.utils.enums import TaskStatusEnum
from src.utils.redis import get_redis
from src.db.core import get_async_session
from src.auth.validations import get_current_user


task_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@task_router.get("/my")
async def owner_tasks(
    user: UserResponse = Depends(get_current_user),
    repo: TaskRepository = Depends(get_task_repo)
):
    """Возвращаетс список задач авторизованного пользователя"""
    return await repo.get_list(owner_id=user.id)

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


