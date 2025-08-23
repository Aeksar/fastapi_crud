from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel
from abc import ABC, abstractmethod
from uuid import UUID
from typing import TypeVar

from src.utils.enums import TaskStatusEnum


TModel = TypeVar("TModel", bound=DeclarativeBase)
TResponse = TypeVar("TResponse", bound=BaseModel)

class BaseCrudRepository(ABC):
    @abstractmethod
    async def get(self, id: UUID) -> TResponse: ...
    
    @abstractmethod
    async def get_list(self, skip: int, limit: int) -> list[TResponse]: ...

    @abstractmethod
    async def update(self, model_id: UUID, model_update: BaseModel) -> TResponse: ...

    @abstractmethod
    async def delete(self, model_id: UUID) -> TResponse: ...

    @abstractmethod
    async def create(self, model_create: BaseModel) -> TResponse: ...

class BaseTaskRepository(BaseCrudRepository):
    @abstractmethod
    async def get_list(self, skip: int, limit: int, status: TaskStatusEnum) -> list[TResponse]: ...
