from sqlalchemy import String, Enum, Date, Boolean, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from uuid import UUID, uuid4
from datetime import date

from src.db.core import Base
from src.utils.enums import TaskStatusEnum, UserRoleEnum


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str] = mapped_column(String(555), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum(TaskStatusEnum),
        default=TaskStatusEnum.CREATED,
        nullable=False
    )
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner = relationship("User", back_populates="tasks")

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, index=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    surname: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    birthdate: Mapped[date] = mapped_column(Date(), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    role: Mapped[Enum] = mapped_column(Enum(UserRoleEnum), default=UserRoleEnum.USER, nullable=False)

    tasks = relationship("Task", back_populates="owner")

