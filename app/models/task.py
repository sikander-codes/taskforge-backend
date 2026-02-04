from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.enums import TaskPriority, TaskStatus
from app.models import Project
from app.models.base import Base
from app.utils.uuid import uuid7


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid7)
    project_id: Mapped[UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=TaskStatus.TODO,
        nullable=False,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority, values_callable=lambda obj: [e.value for e in obj]),
        default=TaskPriority.MEDIUM,
        nullable=False,
    )
    assigned_to: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    project: Mapped["Project"] = relationship("Project")
