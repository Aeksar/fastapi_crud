from sqlalchemy import String, Enum
from sqlalchemy.orm import mapped_column, Mapped
from uuid import UUID

from src.db.core import Base
from src.utils.enums import TaskStatusEnum


class Task(Base):
    __tablename__ = "task"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(String(555), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(TaskStatusEnum),
        default=TaskStatusEnum.CREATED,
        nullable=False
    )

