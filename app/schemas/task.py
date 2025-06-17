"""Pydantic-схемы для задач.

Содержит схемы:
- TaskCreate: для создания задач;
- TaskRead: для возврата задач клиенту;
- TaskUpdate: для обновления задач;
- StatusEnum: перечисление допустимых статусов задач.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict


class StatusEnum(str, Enum):
    """
    Перечисление возможных статусов задачи.

    Значения:
        NEW: Новая задача.
        IN_PROGRESS: Задача в процессе выполнения.
        COMPLETED: Завершённая задача.
    """
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class TaskCreate(BaseModel):
    """
    Схема для создания задачи.

    Атрибуты:
        title (str): Название задачи.
        description (Optional[str]): Описание задачи.
        status (Optional[StatusEnum]): Статус задачи (по умолчанию "новая").
    """
    title: str
    description: Optional[str] = None
    status: Optional[StatusEnum] = None


class TaskRead(BaseModel):
    """
    Схема для чтения информации о задаче.

    Атрибуты:
        id (int): Уникальный идентификатор задачи.
        title (str): Название задачи.
        description (Optional[str]): Описание задачи.
        status (StatusEnum): Статус задачи.
        user_id (int): Идентификатор пользователя, которому принадлежит задача.
    """
    id: int
    title: str
    description: Optional[str] = None
    status: StatusEnum
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    """
    Схема для обновления задачи.

    Атрибуты:
        title (Optional[str]): Новое название задачи.
        description (Optional[str]): Новое описание задачи.
        status (Optional[StatusEnum]): Новый статус задачи.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[StatusEnum] = None
