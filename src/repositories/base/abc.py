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
    async def get_list(self, skip: int, limit: int, **kwargs) -> list[TResponse]: ...

    @abstractmethod
    async def update(self, model_id: UUID, model_update: BaseModel) -> TResponse: ...

    @abstractmethod
    async def delete(self, model_id: UUID) -> TResponse: ...

    @abstractmethod
    async def create(self, model_create: BaseModel) -> TResponse: ...


class BaseTaskRepository(BaseCrudRepository):
    @abstractmethod
    async def get_list(self, skip: int, limit: int, status: TaskStatusEnum, user_id: UUID) -> list[TResponse]: ...


class BaseUserRepository(BaseCrudRepository):
    
    @abstractmethod
    async def get_by_username(self, username: str) -> TResponse: ...


class BaseAuthRepository(BaseCrudRepository):
    @abstractmethod
    async def registration(self, model_create: TModel) -> TResponse: ...   
    
    @abstractmethod
    async def login(self, username: str, password: str): ...
