# TaskHub 📝

**TaskHub** — это полноценное API-приложение для управления задачами с регистрацией, аутентификацией и разграничением
доступа. Проект построен с использованием FastAPI, SQLAlchemy 2.0, PostgreSQL и Alembic. Протестирован с помощью Pytest
и запускается в Docker.

---

## 🚀 Функциональность

- Регистрация и аутентификация пользователей (JWT + refresh)
- CRUD-операции над задачами, привязанными к пользователю
- Ограничение доступа к задачам по `user_id`
- Защита: только владелец задачи или пользователь может их изменять и удалять
- Асинхронная работа с базой (SQLAlchemy 2.0 + asyncpg)
- Alembic для миграций
- Poetry для зависимостей
- Docker для запуска
- Pytest для тестирования

---

## ⚙️ Как запустить проект

### 1. Клонировать и создать `.env`

- Откройте терминал в папке куда собираетесь клонировать репозиторий и используйте команду ниже ⬇️

```bash
git clone https://github.com/sheeeeeri/python_course_tasks.git
cd python_course_tasks/python_4/taskhub
cp .env.example .env
```

---

### 2. Создать файл `init.sql` для тестовой базы

Перед запуском Docker обязательно создайте в корне проекта файл `init.sql` со следующим содержимым:

```sql
CREATE DATABASE "YOUR_POSTGRES_DB_TEST";
```

⚠️ **Важно:** `YOUR_POSTGRES_DB_TEST` должен совпадать с тем, что у вас указано в `.env` в переменной `POSTGRES_DB`,
только с добавлением `_TEST` на конце.

Этот файл нужен для создания тестовой базы данных при первом запуске контейнера.

---

### 3. Запусти в Docker

```bash
docker compose up -d --build
```

🔁 При запуске:

- База `taskhub` создаётся и мигрируется автоматически
- База `taskhub_test` создаётся из `init.sql`

---

## ✅ Запуск тестов

```bash
docker compose exec web pytest -v
```

📆 Тесты покрывают:

- Авторизацию, refresh-token
- CRUD-операции задач
- Ограничение доступа (чужие задачи)
- Операции с пользователями

---

## 🔄 Полезные команды

**Полный сброс всех контейнеров и баз:**

```bash
docker compose down -v
```

**Обновление миграций:**

```bash
docker compose exec web alembic revision --autogenerate -m "some message"
docker compose exec web alembic upgrade head
```

---

## 🔄 Примечание:

**Если у вас уже запускалась база данных ранее, и вы изменили .env (например, сменили пароль или имя пользователя),
необходимо пересоздать базу:**

```bash
docker compose down -v
docker compose up --build -d
```

---

## 📂 Структура проекта

```
.
├── app/              # Код приложения
│   ├── api/          # Роуты
│   ├── models/       # Модели SQLAlchemy
│   ├── schemas/      # Pydantic-схемы
│   ├── db/, core/    # Конфиг, доступ, JWT
│   └── main.py       # Точка входа
├── alembic/          # Миграции
├── tests/            # Тесты
├── init.sql          # Скрипт создания taskhub_test
├── docker-compose.yml
├── Dockerfile
├── .env / .env.example
└── README.md
```

---

# 💼 Описание эндпоинтов:

## 🔐 Аутентификация и пользователи

### POST /users/register — Регистрация нового пользователя

**Request body:**

```json
{
  "username": "user1",
  "email": "user1@example.com",
  "password": "1234"
}
```

**Response:**

```json
{
  "id": 1,
  "username": "user1",
  "email": "user1@example.com"
}
```

---

### POST /users/login — Авторизация

**Form data:**

- `username`: string
- `password`: string

**Response:**

```json
{
  "access_token": "jwt_token",
  "refresh_token": "jwt_refresh_token",
  "token_type": "bearer"
}
```

---

### POST /users/refresh — Обновление access токена по refresh токену

**Request body:**

```json
{
  "refresh_token": "jwt_refresh_token"
}
```

**Response:**

```json
{
  "access_token": "new_access_token",
  "token_type": "bearer"
}
```

---

### GET /users/me — Получение текущего пользователя

**Response:**

```json
{
  "id": 1,
  "username": "user1",
  "email": "user1@example.com"
}
```

---

### GET /users/{user_id} — Получение пользователя по ID

**Response:**

```json
{
  "id": 1,
  "username": "user1",
  "email": "user1@example.com"
}
```

---

### GET /users — Получение всех пользователей

**Response:**

```json
[
  {
    "id": 1,
    "username": "user1",
    "email": "user1@example.com"
  },
  {
    "id": 2,
    "username": "user2",
    "email": "user2@example.com"
  }
]
```

---

### PUT /users/{user_id} — Обновление пользователя (только самого себя)

**Request body:**

```json
{
  "username": "new_name",
  "email": "new_email@example.com",
  "password": "new_password"
}
```

**Response:**

```json
{
  "message": "Успешное обновление данных пользователя",
  "user": {
    "id": 1,
    "username": "new_name",
    "email": "new_email@example.com"
  }
}
```

---

### DELETE /users/{user_id} — Удаление пользователя

**Response:**

- HTTP 204 No Content

---

## ✅ Задачи

### POST /tasks — Создание новой задачи

**Request body:**

```json
{
  "title": "Задача 1",
  "description": "Описание задачи",
  "status": "NEW"
}
```

**Response:**

```json
{
  "id": 1,
  "title": "Задача 1",
  "description": "Описание задачи",
  "status": "NEW",
  "user_id": 1
}
```

---

### GET /tasks — Получение всех задач текущего пользователя

**Response:**

```json
[
  {
    "id": 1,
    "title": "Задача 1",
    "description": "Описание задачи",
    "status": "NEW",
    "user_id": 1
  }
]
```

---

### GET /tasks/{task_id} — Получение задачи по ID

**Response:**

```json
{
  "id": 1,
  "title": "Задача 1",
  "description": "Описание задачи",
  "status": "NEW",
  "user_id": 1
}
```

---

### PUT /tasks/{task_id} — Обновление задачи по ID

**Request body:**

```json
{
  "title": "Обновлённое название",
  "description": "Новое описание",
  "status": "IN_PROGRESS"
}
```

**Response:**

```json
{
  "id": 1,
  "title": "Обновлённое название",
  "description": "Новое описание",
  "status": "IN_PROGRESS",
  "user_id": 1
}
```

---

### DELETE /tasks/{task_id} — Удаление задачи

**Response:**

- HTTP 204 No Content

---

## 👤 Автор

**Alisher K.** — курс "Оффер под ключ", финальный проект.