from os import environ
from pathlib import Path

from dotenv import load_dotenv
from pydantic import ConfigDict, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_PATH_PROJECT = Path(__file__).resolve().parent.parent.parent.joinpath("build", "html")
BASE_PATH = BASE_PATH_PROJECT.parent
load_dotenv(BASE_PATH.joinpath(".env"))
APP_ENV = environ.get("APP_ENV")


class Settings(BaseSettings):
    """
    Клас для завантаження конфігураційних параметрів додатку.

    Attributes:
        app_mode (str): Режим роботи додатку.
        app_name (str): Назва додатку.
        app_host (str): Хост додатку.
        app_port (int): Порт додатку.
        sqlalchemy_database_url (str): URL бази даних SQLAlchemy.
        token_secret_key (str): Секретний ключ для генерації токенів.
        token_algorithm (str): Алгоритм шифрування для токенів.
        mail_username (str): Ім'я користувача для поштового сервера.
        mail_password (str): Пароль для поштового сервера.
        mail_from (str): Email-адреса відправника.
        mail_port (int): Порт поштового сервера.
        mail_server (str): Сервер поштового обслуговування.
        mail_from_name (str): Ім'я відправника пошти.
        redis_host (str): Хост сервера Redis.
        redis_port (int): Порт сервера Redis.
        cloudinary_name (str): Назва для сервісу Cloudinary.
        cloudinary_api_key (str): API-ключ Cloudinary.
        cloudinary_api_secret (str): Секретний ключ Cloudinary.
        rate_limiter_times (int): Кількість спроб доступу за обмежений період часу.
        rate_limiter_seconds (int): Кількість секунд обмеження спроб доступу.
    """

    app_mode: str = "prod"
    app_version: str = "homework"
    app_name: str = "contacts"
    app_host: str = "0.0.0.0"
    app_port: int = 9000
    sqlalchemy_database_url: str = "postgresql://POSTGRES_USERNAME:POSTGRES_PASSWORD@POSTGRES_HOST/POSTGRES_DATABASE"
    token_secret_key: str = "some_SuPeR_key"
    token_algorithm: str = "HS256"
    mail_username: str = "user@example.com"
    mail_password: str = ""
    mail_from: str = "user@example.com"
    mail_port: int = 465
    mail_server: str = ""
    mail_from_name: str = ""
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    cloudinary_name: str = "some_name"
    cloudinary_api_key: str = "0000000000000"
    cloudinary_api_secret: str = "some_secret"
    rate_limiter_times: int = 2
    rate_limiter_seconds: int = 5
    SPHINX_DIRECTORY: str = str(BASE_PATH_PROJECT)
    STATIC_DIRECTORY: str = str(BASE_PATH_PROJECT)


    class Config:
        """
        Конфігурація класу Settings.

        Attributes:
            extra (str): Поведінка з додатковими полями.
            env_file (str): Шлях до файлу .env.
            env_file_encoding (str): Кодування файлу .env.
        """
        extra = "ignore"
        # TESTED FIRST USED ENV variables, even if file defined.
        env_file = BASE_PATH.joinpath(f".env-{APP_ENV}") if APP_ENV else BASE_PATH.joinpath(".env")
        env_file_encoding = "utf-8"


settings = Settings()

if __name__ == "__main__":
    print(settings.Config.env_file)
    print(settings)
