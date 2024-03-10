from sqlalchemy import Boolean, Column, Date, DateTime, Integer, String, Text, func, Enum, ForeignKey
from datetime import date
import enum
from sqlalchemy.orm import declarative_base, relationship

Base: object = declarative_base()

class Role(enum.Enum):
    """
    Роль користувача.

    Attributes:
        admin: Роль адміністратора.
        moderator: Роль модератора.
        user: Роль звичайного користувача.
    """
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"

class User(Base):
    """
    Модель користувача.

    Attributes:
        id: Ідентифікатор користувача.
        username: Ім'я користувача.
        email: Email користувача.
        password: Пароль користувача.
        refresh_token: Токен оновлення.
        avatar: Аватар користувача.
        role: Роль користувача.
    """
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True)
    username: str = Column(String(150), nullable=False)
    email: str = Column(String(150), nullable=False, unique=True)
    password: str = Column(String(255), nullable=False)
    refresh_token: str = Column(String(255), nullable=True)
    avatar: str = Column(String(255), nullable=True)
    role: Enum = Column("roles", Enum(Role), default=Role.user)

    def __str__(self):
        """
        Представлення об'єкта користувача у вигляді рядка.
        """
        return f"id: {self.id}, email: {self.email}, username: {self.username}"

class Contact(Base):
    """
    Модель контакту.

    Attributes:
        id: Ідентифікатор контакту.
        first_name: Ім'я контакту.
        last_name: Прізвище контакту.
        email: Email контакту.
        phone: Номер телефону контакту.
        birthday: Дата народження контакту.
        comments: Коментарі до контакту.
        favorite: Ознака вибраності контакту.
        created_at: Дата створення запису.
        updated_at: Дата останнього оновлення запису.
        user_id: Ідентифікатор користувача, якому належить контакт.
    """
    __tablename__ = "contacts"

    id: int = Column(Integer, primary_key=True, index=True)
    first_name: str = Column(String)
    last_name: str = Column(String)
    email: str = Column(String)
    phone: str = Column(String)
    birthday: date = Column(Date)
    comments: str = Column(Text)
    favorite: bool = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    user_id: int = Column(Integer, ForeignKey("users.id"), nullable=False, default=1)
    user = relationship("User", backref="contacts")
