from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy import select, update, delete
from uuid import UUID
from typing import Optional

from src.repositories.abc import BaseTaskRepository
from src.db import Task
from src.utils.enums import TaskStatusEnum
from src.api.models.task import TaskResponse, TaskCreate, TaskUpdate
from src.exc.api import NotFoundException
from src.settings import logger

__all__ = ["TaskRepository", "get_task_repo"]

class TaskRepository(BaseTaskRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: UUID) -> TaskResponse:
        try:
            task = await self.session.get_one(Task, id)
            return TaskResponse.model_validate(task, from_attributes=True)
        except NoResultFound:
            raise NotFoundException("task")
        except SQLAlchemyError as e:
            logger.error(f"Error with get task: {e}")
            raise
        
    async def get_list(
            self,
            skip: int = 0,
            limit: int = 50,
            status: Optional[TaskStatusEnum] = None
        ) -> list[TaskResponse]:
        try:
            query = select(Task).offset(skip).limit(limit)
            if status:
                query = query.where(Task.status == status)
            result = await self.session.scalars(query)
            tasks = result.all()
            return tasks
        except SQLAlchemyError as e:
            logger.error(f"Error with get_list task: {e}")
            raise
    
    async def update(self, task_id: UUID, task_update: TaskUpdate) -> TaskResponse:
        try:
            async with self.session.begin():
                update_data = task_update.model_dump(exclude_unset=True)
                query = update(Task).where(Task.id == task_id).values(**update_data).returning(Task)
                result = await self.session.execute(query)
                return TaskResponse.model_validate(result.scalar_one())
        except NoResultFound:
            raise NotFoundException("task")
        except SQLAlchemyError as e:
            logger.error(f"Error with update task {task_id}: {e}")
            raise
        
    async def delete(self, task_id: UUID) -> TaskResponse:
        try:
            async with self.session.begin():
                query = delete(Task).where(Task.id == task_id).returning(Task)
                result = await self.session.execute(query)
                return TaskResponse.model_validate(result.scalar_one())
        except NoResultFound as e:
            raise NotFoundException("task")
        except SQLAlchemyError as e:
            logger.error(f"Error with delete task {task_id}: {e}")
            raise

    async def create(self, task_create: TaskCreate) -> TaskResponse:
        try:
            new_task_dict = task_create.model_dump(exclude_unset=True)
            new_task = Task(**new_task_dict)
            self.session.add(new_task)
            await self.session.commit()
            await self.session.refresh(new_task)
            return new_task
        except Exception as e:
            logger.error(f"Error with create task: {e}")
            await self.session.rollback()
            raise