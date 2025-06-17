"""
Модель задач для системы управления задачами.

Содержит информацию о задачах, привязанных к пользователям: название, описание и связь с пользователем.
"""

from enum import Enum as PyEnum

from sqlalchemy import String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class StatusEnum(PyEnum):
    """
    Перечисление статусов задачи.

    Возможные значения:
        NEW: Новая задача.
        IN_PROGRESS: Задача в процессе выполнения.
        COMPLETED: Завершённая задача.
    """
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class Task(Base):
    """
    Модель таблицы задач.

    Атрибуты:
        id (int): Уникальный идентификатор задачи.
        title (str): Название задачи.
        description (str | None): Описание задачи (необязательное поле).
        status (StatusEnum): Статус задачи.
        user_id (int): Идентификатор пользователя, которому принадлежит задача.
        user (User): Объект пользователя, связанный с задачей.
    """
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(300))
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, name="status_enum", create_constraint=True),
        nullable=False,
        default=StatusEnum.NEW.value
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="tasks")
