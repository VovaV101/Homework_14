from datetime import datetime

from pydantic import BaseModel


class AccessTokenRefreshResponse(BaseModel):
    """
    Модель відповіді на оновлення токена доступу.

    Attributes:
        token_type (str): Тип токена, за замовчуванням "bearer".
        access_token (str): Токен доступу.
        expire_access_token (datetime): Дата та час закінчення терміну дії токена доступу.
        refresh_token (str): Токен оновлення.
        expire_refresh_token (datetime): Дата та час закінчення терміну дії токена оновлення.
    """
    token_type: str = "bearer"
    access_token: str
    expire_access_token: datetime
    refresh_token: str
    expire_refresh_token: datetime


class AccessTokenResponse(BaseModel):
    """
    Модель відповіді на запит токена доступу.

    Attributes:
        access_token (str): Токен доступу.
        token_type (str): Тип токена, за замовчуванням "bearer".
    """
    access_token: str
    token_type: str = "bearer"
