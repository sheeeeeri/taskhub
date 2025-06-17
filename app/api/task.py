"""Маршруты API для управления задачами: создание, просмотр, обновление и удаление задач."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.dependencies import get_async_session, get_current_user
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter(tags=["Tasks"])


async def get_task_checked(
        task_id: int,
        session: AsyncSession,
        current_user: User,
) -> Task:
    """
    Получение задачи и проверка прав доступа.

    Аргументы:
        task_id (int): Идентификатор задачи.
        session (AsyncSession): Сессия БД.
        current_user (User): Аутентифицированный пользователь.

    Возвращает:
        Task: Объект задачи, если доступ разрешён.

    Исключения:
        HTTPException: 404 — задача не найдена; 403 — нет прав.
    """
    task = await session.get(Task, task_id)

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задача не найдена")

    if task.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Недостаточно прав доступа")

    return task


@router.post("/tasks", status_code=status.HTTP_201_CREATED, summary="Создание задачи")
async def create_task(
        task: TaskCreate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
) -> TaskRead:
    """
    Создание новой задачи для текущего пользователя.

    Аргументы:
        task (TaskCreate): Данные задачи.
        session (AsyncSession): Сессия базы данных.
        current_user (User): Аутентифицированный пользователь.

    Возвращает:
        TaskRead: Данные созданной задачи.
    """
    new_task = Task(
        title=task.title,
        description=task.description,
        status=task.status if task.status else None,
        user_id=current_user.id
    )

    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)

    return TaskRead.model_validate(new_task)


@router.get("/tasks", summary="Получение всех задач пользователя")
async def read_tasks(
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
) -> list[TaskRead]:
    """
    Получение списка всех задач текущего пользователя.

    Аргументы:
        session (AsyncSession): Сессия базы данных.
        current_user (User): Аутентифицированный пользователь.

    Возвращает:
        list[TaskRead]: Список задач пользователя.
    """
    result = await session.execute(
        select(Task).where(Task.user_id == current_user.id)
    )
    tasks = result.scalars().all()

    return [TaskRead.model_validate(task) for task in tasks]


@router.get("/tasks/{task_id}", summary="Получение задачи по ID")
async def read_task(
        task_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
) -> TaskRead:
    """
    Получение задачи по её ID для текущего пользователя.

    Аргументы:
        task_id (int): Идентификатор задачи.
        session (AsyncSession): Сессия базы данных.
        current_user (User): Аутентифицированный пользователь.

    Возвращает:
        TaskRead: Данные задачи.

    Исключения:
        HTTPException: 404 если задача не найдена, 403 если нет прав доступа.
    """
    task = await get_task_checked(task_id, session, current_user)

    return TaskRead.model_validate(task)


@router.put("/tasks/{task_id}", summary="Обновление задач по ID")
async def update_task(
        task_id: int,
        task_update: TaskUpdate,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
) -> TaskRead:
    """
    Обновление задачи по её ID.

    Аргументы:
        task_id (int): Идентификатор задачи.
        task_update (TaskUpdate): Обновленные данные задачи.
        session (AsyncSession): Сессия базы данных.
        current_user (User): Аутентифицированный пользователь.

    Возвращает:
        TaskRead: Обновленные данные задачи.

    Исключения:
        HTTPException: 404 если задача не найдена, 403 если нет прав доступа.
    """
    task = await get_task_checked(task_id, session, current_user)

    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status

    await session.commit()
    await session.refresh(task)

    return TaskRead.model_validate(task)


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удаление задачи по её ID")
async def delete_task(
        task_id: int,
        session: AsyncSession = Depends(get_async_session),
        current_user: User = Depends(get_current_user)
) -> None:
    """
    Удаление задачи по её ID.

    Аргументы:
        task_id (int): Идентификатор задачи.
        session (AsyncSession): Сессия базы данных.
        current_user (User): Аутентифицированный пользователь.

    Исключения:
        HTTPException: 404 если задача не найдена, 403 если нет прав доступа.
    """
    task = await get_task_checked(task_id, session, current_user)

    await session.delete(task)
    await session.commit()
