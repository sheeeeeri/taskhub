"""
Настройка подключения к базе данных с использованием SQLAlchemy Async.

Содержит:
- URL подключения, формируемый из переменных окружения;
- асинхронный движок SQLAlchemy;
- фабрику асинхронных сессий;
- базовый класс для ORM-моделей.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.core.config import settings

DATABASE_URL = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.POSTGRES_DB}"
)

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()
