from datetime import date, datetime
from pydantic import BaseModel, Field, EmailStr

from ..shemas.users import UserResponse


class ContactModel(BaseModel):
    """
    Модель контакту для створення або оновлення.

    Attributes:
        first_name (str): Ім'я контакту.
        last_name (str): Прізвище контакту.
        email (EmailStr): Електронна адреса контакту.
        phone (str, optional): Номер телефону контакту.
        birthday (date, optional): День народження контакту.
        comments (str, optional): Додаткові дані про контакт.
        favorite (bool): Позначка улюбленого контакту.
    """
    first_name: str = Field(
        default="",
        examples=["Taras", "Ostap"],
        min_length=1,
        max_length=25,
        title="Ім'я",
    )
    last_name: str = Field(
        default="",
        examples=["Shevcheko", "Bulba"],
        min_length=1,
        max_length=25,
        title="Прізвище",
    )
    email: EmailStr
    phone: str | None = Field(
        None,
        examples=["+380 44 123-4567", "+380 (44) 1234567", "+380441234567"],
        max_length=25,
        title="Номер телефону",
    )
    birthday: date | None = None
    comments: str | None = Field(default=None, title="Додаткові дані")
    favorite: bool = False


class ContactFavoriteModel(BaseModel):
    """
    Модель для оновлення позначки "улюблений" контакту.

    Attributes:
        favorite (bool): Позначка "улюблений".
    """
    favorite: bool = False


class ContactResponse(BaseModel):
    """
    Модель відповіді з інформацією про контакт.

    Attributes:
        id (int): Ідентифікатор контакту.
        first_name (str, optional): Ім'я контакту.
        last_name (str, optional): Прізвище контакту.
        email (EmailStr, optional): Електронна адреса контакту.
        phone (str, optional): Номер телефону контакту.
        birthday (date, optional): День народження контакту.
        comments (str, optional): Додаткові дані про контакт.
        favorite (bool): Позначка "улюблений".
        created_at (datetime): Дата та час створення контакту.
        updated_at (datetime): Дата та час оновлення контакту.
        user (UserResponse): Інформація про користувача.
    """
    id: int
    first_name: str | None
    last_name: str | None
    email: EmailStr | None
    phone: str | None
    birthday: date | None
    comments: str | None
    favorite: bool
    created_at: datetime
    updated_at: datetime
    user: UserResponse

    class Config:
        from_attributes = True
