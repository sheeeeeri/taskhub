"""Pydantic-схемы, используемые для операций с пользователями."""

from typing import Optional

from pydantic import BaseModel, EmailStr, SecretStr


class UserCreate(BaseModel):
    """
    Схема для создания пользователя.

    Атрибуты:
        username (str): Имя пользователя.
        email (EmailStr): Электронная почта пользователя.
        password (str): Пароль пользователя.
    """
    username: str
    email: EmailStr
    password: SecretStr


class UserRead(BaseModel):
    """
    Схема для чтения информации о пользователе.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        username (str): Имя пользователя.
        email (EmailStr): Электронная почта пользователя.
    """
    id: int
    username: str
    email: EmailStr

    class Config:
        """
        Конфигурация для поддержки работы с ORM.

        from_attributes (bool): Использовать атрибуты ORM для сериализации.
        """
        from_attributes = True


class UpdateUserRequest(BaseModel):
    """
    Схема для обновления пользователя.

    Атрибуты:
        username (Optional[str]): Новое имя пользователя.
        email (Optional[EmailStr]): Новая электронная почта.
        password (Optional[SecretStr]): Новый пароль пользователя.
    """
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[SecretStr] = None


class UpdateUserResponse(BaseModel):
    """
    Схема ответа при успешном обновлении пользователя.

    Атрибуты:
        message (str): Сообщение об успешном обновлении.
        user (UserRead): Обновлённые данные пользователя.
    """
    message: str
    user: UserRead
