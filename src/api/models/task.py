from pydantic import BaseModel, Field
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

    class Config:
        from_attributes = True