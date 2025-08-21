from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from uuid import UUID

from src.utils.enums import TaskStatusEnum

class TaskBase(BaseModel):
    name: str = Field(max_length=150, min_length=1)
    description: Optional[str] = Field(default=None, max_length=555)
    status: TaskStatusEnum = Field(default=TaskStatusEnum.CREATED)

class TaskCreate(TaskBase):
    ...

class TaskUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=150, min_length=1)
    description: Optional[str] = Field(default=None, max_length=555)
    status: Optional[TaskStatusEnum] = Field(default=None)

class TaskResponse(TaskBase):
    id: UUID

    model_config = ConfigDict(from_attributes=True)