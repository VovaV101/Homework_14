from pydantic import BaseModel, Field, EmailStr
from ..database.models import Role


class UserModel(BaseModel):
    """
    Модель користувача для реєстрації.

    Attributes:
        username (str): Ім'я користувача.
        email (EmailStr): Електронна адреса користувача.
        password (str): Пароль користувача.
    """
    username: str = Field(min_length=2, max_length=150)
    email: EmailStr
    password: str = Field(min_length=6, max_length=64)


class NewUserResponse(BaseModel):
    """
    Модель відповіді на створення нового користувача.

    Attributes:
        username (str): Ім'я користувача.
    """
    username: str


class UserResponse(BaseModel):
    """
    Модель відповіді на запит даних користувача.

    Attributes:
        id (int): Ідентифікатор користувача.
        username (str): Ім'я користувача.
        email (str): Електронна адреса користувача.
        avatar (str, optional): URL аватара користувача, за замовчуванням None.
        role (Role): Роль користувача.
    """
    id: int
    username: str
    email: str
    avatar: str | None
    role: Role

    class Config:
        from_attributes = True
