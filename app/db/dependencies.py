"""
Модуль зависимостей для работы с базой данных и аутентификацией пользователей.

Содержит:
- Получение асинхронной сессии SQLAlchemy;
- Получение текущего пользователя по JWT токену;
- Обработку ошибок валидации токена и доступа.
"""

from typing import AsyncGenerator

from fastapi import Depends
from fastapi import HTTPException, status
from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import async_session_factory
from app.models.user import User


class CustomHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        try:
            return await super().__call__(request)
        except HTTPException as exc:
            # Меняем 403 на 401
            if exc.status_code == status.HTTP_403_FORBIDDEN:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Необходимо указать токен авторизации"
                )
            raise exc


security = CustomHTTPBearer()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Получение асинхронной сессии базы данных.

    Возвращает:
        AsyncGenerator[AsyncSession, None]: Генератор асинхронной сессии для работы с БД.
    """
    async with async_session_factory() as session:
        yield session


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_async_session)
) -> User:
    """
    Получение текущего аутентифицированного пользователя по токену.

    Аргументы:
        credentials (HTTPAuthorizationCredentials): Авторизационные данные (заголовок Authorization).
        session (AsyncSession): Сессия БД.

    Возвращает:
        User: Объект пользователя, если токен валиден и пользователь существует.

    Исключения:
        HTTPException: 401 ошибка, если токен недействителен, истёк или пользователь не найден.
    """
    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = int(payload.get("sub"))
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истёк"
        )
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось проверить токен"
        )

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )

    return user
