"""
Модуль конфигурации приложения.

Считывает переменные окружения из файла `.env` и предоставляет доступ к настройкам
базы данных и параметрам безопасности через объект `settings`.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Класс настроек, автоматически загружающий значения из переменных окружения.

    Атрибуты:
        SECRET_KEY (str): Секретный ключ для подписи JWT.
        ALGORITHM (str): Алгоритм шифрования для JWT (например, HS256).
        ACCESS_TOKEN_EXPIRE_MINUTES (int): Время жизни для токена в минутах.
        DB_HOST (str): Хост базы данных.
        DB_PORT (int): Порт базы данных.
        POSTGRES_DB (str): Имя базы данных.
        POSTGRES_USER (str): Имя пользователя базы данных.
        POSTGRES_PASSWORD (str): Пароль от базы данных.
    """
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int
    DB_HOST: str
    DB_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    class Config:
        """
        Конфигурация загрузки переменных окружения.

        Атрибуты:
            env_file (str): Имя файла, из которого загружаются переменные.
        """
        env_file = ".env"


settings = Settings()
