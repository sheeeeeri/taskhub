"""Главная точка входа в приложение FastAPI. Регистрирует маршруты приложения."""

from fastapi import FastAPI

from app.api.task import router as tasks_router
from app.api.user import router as users_router

app = FastAPI(
    title="TaskHub API",
    description="API для управления задачами и пользователями",
)

app.include_router(users_router)
app.include_router(tasks_router)
