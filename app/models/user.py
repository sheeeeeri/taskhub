"""
Модель пользователя для системы управления задачами.

Содержит информацию о пользователе: имя пользователя, электронную почту,
захешированный пароль и связь с задачами пользователя.
"""

from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.task import Task


class User(Base):
    """
    Модель таблицы пользователей.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        username (str): Имя пользователя, должно быть уникальным.
        email (str): Электронная почта пользователя, должна быть уникальной.
        hashed_password (str): Захешированный пароль (не в открытом виде), хранится в БД.
        tasks (List[Task]): Список задач, связанных с пользователем.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)

    tasks: Mapped[List["Task"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
