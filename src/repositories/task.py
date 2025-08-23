from src.repositories.base.abc import BaseTaskRepository
from src.repositories.base.crud import CrudRepository
from src.utils.enums import TaskStatusEnum
from src.api.models.task import TaskResponse
from src.db import Task


__all__ = ["TaskRepository", "BaseTaskRepository"]


class TaskRepository(CrudRepository, BaseTaskRepository):
    model = Task
    response_model = TaskResponse

    async def get_list(self, skip, limit, status):
        tasks: list[Task] = await super().get_list(skip, limit)
        response = []
        if status:
            for task in tasks:
                if task.status == status:
                    response.append(task)
            return response
        return tasks
    

