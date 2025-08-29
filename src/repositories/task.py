from src.repositories.base.abc import BaseTaskRepository
from src.repositories.base.crud import CrudRepository
from src.api.models.task import TaskResponse
from src.db import Task


__all__ = ["TaskRepository", "BaseTaskRepository"]


class TaskRepository(CrudRepository, BaseTaskRepository):
    model = Task
    response_model = TaskResponse
