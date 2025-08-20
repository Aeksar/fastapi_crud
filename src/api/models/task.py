from pydantic import BaseModel, Field
from typing import Annotated, Optional
from uuid import UUID

from src.utils.enums import TaskStatusEnum

IDField = Field(..., description="Уникальный идентификатор задачи")
NameField = Field(max_length=150, min_length=1, description="Название задачи")
DescField = Field(max_length=555, default=None, description="Описание задачи")
StatusField = Field(default=TaskStatusEnum.CREATED, description="Статус задачи")

class TaskModel(BaseModel):
    id: UUID = IDField
    name: str = NameField
    description: Optional[str] = DescField
    status: TaskStatusEnum = StatusField


class TaskUpdateModel(BaseModel):
    name: Optional[str] = NameField
    description: Optional[str] = DescField
    status: Optional[TaskStatusEnum] = StatusField


class TaskCreateModel(BaseModel):
    name: str = NameField
    description: Optional[str] = DescField
    status: TaskStatusEnum = StatusField