"""Фикстуры и вспомогательные функции для тестирования FastAPI-приложения."""

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings
from app.db.database import Base
from app.db.dependencies import get_async_session
from app.main import app


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    """
    Создаёт тестового клиента с отдельной тестовой базой данных.

    Возвращает:
        AsyncClient: Клиент для выполнения запросов к приложению.
    """
    TEST_DATABASE_URL = (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.POSTGRES_DB}_test"
    )

    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_async_session():
        async with SessionLocal() as session:
            yield session

    # Создание схемы базы данных
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Подмена зависимости в приложении на тестовую сессию
    app.dependency_overrides[get_async_session] = override_get_async_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


async def register_and_login(client: AsyncClient, username: str, email: str, password: str) -> str:
    """
    Регистрирует и логинит пользователя. Возвращает access_token.

    Аргументы:
        client (AsyncClient): Тестовый HTTP-клиент.
        username (str): Имя пользователя.
        email (str): Электронная почта.
        password (str): Пароль.

    Возвращает:
        str: JWT токен доступа.
    """
    register_response = await client.post("/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    assert register_response.status_code == 201

    login_response = await client.post("/users/login", data={
        "username": username,
        "password": password
    })
    assert login_response.status_code == 200

    token_data = login_response.json()
    assert "access_token" in token_data
    return token_data["access_token"]
