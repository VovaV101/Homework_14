from libgravatar import Gravatar
from sqlalchemy.orm import Session

from ..shemas.users import UserModel
from ..database.models import User


async def create_user(body: UserModel, db: Session) -> User | None:
    """
    Створює нового користувача з вказаними даними.

    Args:
        body (UserModel): Об'єкт моделі користувача.
        db (Session): Сесія бази даних.

    Returns:
        User | None: Створений користувач або None, якщо створення не вдалося.
    """
    try:
        g = Gravatar(body.email)
        new_user = User(**body.model_dump(), avatar=g.get_image())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception:
        return None
    return new_user


async def get_user_by_email(email: str | None, db: Session) -> User | None:
    """
    Отримує користувача за електронною адресою.

    Args:
        email (str | None): Електронна адреса користувача.
        db (Session): Сесія бази даних.

    Returns:
        User | None: Знайдений користувач або None, якщо не знайдено.
    """
    if email:
        try:
            return db.query(User).filter_by(email=email).first()
        except Exception:
            ...
    return None


async def get_user_by_name(username: str | None, db: Session) -> User | None:
    """
    Отримує користувача за ім'ям користувача.

    Args:
        username (str | None): Ім'я користувача.
        db (Session): Сесія бази даних.

    Returns:
        User | None: Знайдений користувач або None, якщо не знайдено.
    """
    if username:
        try:
            return db.query(User).filter_by(email=username).first()
        except Exception:
            ...
    return None


async def update_user_refresh_token(
    user: User, refresh_token: str | None, db: Session
) -> str | None:
    """
    Оновлює токен оновлення для користувача.

    Args:
        user (User): Об'єкт користувача.
        refresh_token (str | None): Токен оновлення.
        db (Session): Сесія бази даних.

    Returns:
        str | None: Оновлений токен оновлення або None, якщо оновлення не вдалося.
    """
    if user:
        try:
            user.refresh_token = refresh_token
            db.commit()
            return refresh_token
        except Exception:
            ...
    return None


async def update_by_name_refresh_token(
    username: str | None, refresh_token: str | None, db: Session
) -> str | None:
    """
    Оновлює токен оновлення для користувача за ім'ям користувача.

    Args:
        username (str | None): Ім'я користувача.
        refresh_token (str | None): Токен оновлення.
        db (Session): Сесія бази даних.

    Returns:
        str | None: Оновлений токен оновлення або None, якщо оновлення не вдалося.
    """
    if username and refresh_token:
        try:
            user = await get_user_by_name(username, db)
            return await update_user_refresh_token(user, refresh_token, db)
        except Exception:
            ...
    return None
