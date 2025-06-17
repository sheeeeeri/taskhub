"""
Файл конфигурации Alembic для управления миграциями базы данных.

Содержит настройки для запуска миграций в offline- и online-режимах.
Использует асинхронный движок SQLAlchemy и метаданные из ORM-моделей проекта.
Подключается к базе данных через URL, импортированный из database.py.

Важно: некоторые импорты (модели и Base) используются неявно для корректной генерации миграций.
Не удаляйте их, даже если IDE помечает как неиспользуемые.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.db.database import DATABASE_URL, Base
from app.models import user, task

config = context.config
fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", DATABASE_URL)

target_metadata = Base.metadata


def run_migrations_offline():
    """Запуск миграций в offline-режиме (без подключения к БД)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Настройка и запуск миграций в online-режиме."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Запуск миграций в online-режиме с подключением к БД."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=None,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
