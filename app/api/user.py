"""Маршруты для управления пользователями: регистрация, авторизация, получение, обновление и удаление пользователей."""

from datetime import timedelta

from fastapi import APIRouter, HTTPException, status, Depends, Response, Form
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError
from passlib.hash import bcrypt
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.auth import create_access_token, create_refresh_token
from app.core.config import settings
from app.db.dependencies import get_async_session, get_current_user
from app.models.user import User
from app.schemas.token import RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UpdateUserRequest, UserRead, UpdateUserResponse

router = APIRouter(tags=["Users"])


@router.post("/users/register", status_code=status.HTTP_201_CREATED,
             summary="Регистрация пользователя")
async def register_user(
        user: UserCreate,
        session: AsyncSession = Depends(get_async_session)
) -> UserRead:
    """
    Регистрация нового пользователя.

    Аргументы:
        user (UserCreate): Данные нового пользователя.
        session (AsyncSession): Сессия базы данных.

    Возвращает:
        UserRead: Информация о зарегистрированном пользователе.

    Исключения:
        HTTPException: 409, если пользователь с таким email или username уже существует.
    """
    stmt = select(User).where((User.email == user.email) | (User.username == user.username))
    result = await session.execute(stmt)

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email или именем уже существует"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=bcrypt.hash(user.password.get_secret_value())
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return UserRead.model_validate(new_user)


@router.post("/users/login", summary="Авторизация пользователя")
async def login(
        username: str = Form(...),
        password: str = Form(...),
        session: AsyncSession = Depends(get_async_session)
) -> dict:
    """
    Авторизация пользователя и получение JWT access и refresh токенов.

    Аргументы:
        username (str): Имя пользователя.
        password (str): Пароль пользователя.
        session (AsyncSession): Сессия базы данных.

    Возвращает:
        dict: Словарь с access и refresh токенами, а также типом токена.

    Исключения:
        HTTPException: 401, если имя пользователя или пароль неверны.
    """
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    existing_user = result.scalar_one_or_none()

    if not existing_user or not bcrypt.verify(password, existing_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )

    token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token(
        data={"sub": str(existing_user.id)},
        expires_delta=token_expires
    )

    refresh_token = create_refresh_token(
        data={"sub": str(existing_user.id)},
        expires_delta=refresh_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/users/refresh", summary="Обновление access токена по refresh токену")
async def refresh_token(
        request: RefreshTokenRequest,
        session: AsyncSession = Depends(get_async_session)
) -> TokenResponse:
    """
    Обновление access токена по действующему refresh токену.

    Аргументы:
        request (RefreshTokenRequest): Объект с refresh токеном.
        session (AsyncSession): Сессия базы данных.

    Возвращает:
        TokenResponse: Новый access токен и его тип.

    Исключения:
        HTTPException: 401, если токен истёк, недействителен или пользователь не найден.
    """
    try:
        payload = jwt.decode(request.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = int(payload.get("sub"))
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Срок действия refresh токена истёк")
    except (JWTError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный refresh токен")

    user = await session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")

    access_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_expires)

    return TokenResponse(access_token=new_access_token, token_type="bearer")


@router.get("/users/me", summary="Получение текущего пользователя")
async def read_users_me(current_user: User = Depends(get_current_user)) -> UserRead:
    """
    Получение информации о текущем авторизованном пользователе.

    Аргументы:
        current_user (User): Объект текущего пользователя.

    Возвращает:
        UserRead: Данные текущего пользователя.
    """
    return UserRead.model_validate(current_user)


@router.get("/users/{user_id}", summary="Получение пользователя по ID")
async def get_user(
        user_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
) -> UserRead:
    """
    Получение информации о пользователе по его ID (только самому себе).

    Аргументы:
        user_id (int): Идентификатор пользователя.
        current_user (User): Текущий пользователь.
        session (AsyncSession): Сессия базы данных.

    Возвращает:
        UserRead: Данные пользователя.

    Исключения:
        HTTPException: 404, если пользователь не найден.
    """
    user = await session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    return UserRead.model_validate(user)


@router.get("/users", summary="Получение всех пользователей")
async def get_users(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user),
) -> list[UserRead]:
    """
    Получение списка всех пользователей.

    Аргументы:
        session (AsyncSession): Сессия базы данных.
        current_user (User): Аутентифицированный пользователь.

    Возвращает:
        list[UserRead]: Список пользователей.
    """
    result = await session.execute(select(User))
    users = result.scalars().all()
    return [UserRead.model_validate(user) for user in users]


@router.put("/users/{user_id}", summary="Обновление пользователя по ID")
async def update_user(
        user_id: int,
        user_update: UpdateUserRequest,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
) -> UpdateUserResponse:
    """
    Обновление данных пользователя по его ID (только самому себе).

    Аргументы:
        user_id (int): Идентификатор пользователя.
        user_update (UpdateUserRequest): Обновлённые данные.
        current_user (User): Текущий пользователь.
        session (AsyncSession): Сессия базы данных.

    Возвращает:
        UpdateUserResponse: Результат обновления.

    Исключения:
        HTTPException: 403 при попытке обновить чужие данные, 404 если пользователь не найден,
        409 при попытке использовать уже занятый username/email.

    """
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")

    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    for field, value in user_update.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    try:
        await session.commit()
    except IntegrityError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Имя пользователя или email уже заняты"
        )

    await session.refresh(user)

    return UpdateUserResponse(
        message="Успешное обновление данных пользователя",
        user=UserRead.model_validate(user)
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удаление пользователя по ID")
async def delete_user(
        user_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_async_session)
) -> None:
    """
    Удаление пользователя по его ID (только самому себе).

    Аргументы:
        user_id (int): Идентификатор пользователя.
        current_user (User): Текущий пользователь.
        session (AsyncSession): Сессия базы данных.

    Возвращает:
        Response: Ответ с кодом 204 при успешном удалении.

    Исключения:
        HTTPException: 403 при попытке удалить чужой аккаунт, 404 если пользователь не найден.
    """
    if user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Доступ запрещён")

    user = await session.get(User, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    await session.delete(user)
    await session.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
