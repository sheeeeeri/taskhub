"""
Утилита для создания JWT токенов доступа.

Используется для генерации токена авторизации с заданным временем жизни (exp),
включающего произвольные данные, такие как идентификатор пользователя.

Формирует токен с учётом часового пояса (UTC) и кодирует его с использованием
секретного ключа и алгоритма из настроек проекта.
"""

import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings


def create_access_token(data: dict,
                        expires_delta: timedelta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)) -> str:
    """
    Создание JWT токена с истечением срока действия.

    Аргументы:
        data (dict): Данные, которые будут зашифрованы.
        expires_delta (timedelta): Время жизни токена.

    Возвращает:
        str: JWT токен.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp": expire,
        "jti": str(uuid.uuid4())  # уникальный идентификатор токена
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict,
                         expires_delta: timedelta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)) -> str:
    """
    Создание JWT refresh токена.

    Аргументы:
        data (dict): Данные для кодирования (обычно {'sub': user_id}).
        expires_delta (timedelta): Срок действия refresh-токена.

    Возвращает:
        str: Refresh-токен.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
