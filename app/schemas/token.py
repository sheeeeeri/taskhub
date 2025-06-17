"""Pydantic-схемы для токенов.

Содержит схемы для создания и обновления токена.
"""

from pydantic import BaseModel


class RefreshTokenRequest(BaseModel):
    """
    Схема запроса на обновление access токена.

    Атрибуты:
        refresh_token (str): Действующий refresh токен.
    """
    refresh_token: str


class TokenResponse(BaseModel):
    """
    Схема ответа с access и refresh токенами.

    Атрибуты:
        access_token (str): Access токен.
        refresh_token (str | None): Refresh токен, если выдается.
        token_type (str): Тип токена.
    """
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
