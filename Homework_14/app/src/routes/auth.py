from typing import Annotated, Any
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Response,
    Security,
    status,
    Cookie,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from ..database.db import get_db
from ..database.models import User
from ..shemas.users import UserResponse, UserModel
from ..repository import auth as repository_auth
from ..repository import users as repository_users


router = APIRouter(prefix="", tags=["Auth"])

security = HTTPBearer()

SET_COOKIES = False


@router.post(
    "/signup",
    response_model=UserResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def signup(body: UserModel, db: Session = Depends(get_db)):
    """
    Реєструє нового користувача.

    Args:
        body (UserModel): Дані нового користувача.
        db (Session): Сесія бази даних.

    Returns:
        UserResponse: Відповідь з даними про нового користувача.
    """
    new_user = await repository_auth.signup(body=body, db=db)
    if new_user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    return new_user


@router.post("/login", response_model=repository_auth.auth_service.token_response_model)
async def login(
    response: Response,
    body: Annotated[repository_auth.auth_service.auth_response_model, Depends()],
    db: Session = Depends(get_db),
):
    """
    Виконує процес авторизації користувача.

    Args:
        response (Response): Об'єкт відповіді.
        body (repository_auth.auth_service.auth_response_model): Дані авторизації.
        db (Session): Сесія бази даних.

    Returns:
        Any: Дані авторизації користувача.
    """
    token = await repository_auth.login(
        username=body.username, password=body.password, db=db
    )
    if token is None:
        exception_data = {
            "status_code": status.HTTP_401_UNAUTHORIZED,
            "detail": "Invalid credentianal",
        }
        if SET_COOKIES:
            response.delete_cookie(key="access_token", httponly=True, path="/api/")
            exception_data.update(
                {
                    "headers": {
                        "set-cookie": response.headers.get("set-cookie", ""),
                    }
                }
            )
        raise HTTPException(**exception_data)
    refresh_token = token.get("refresh_token")
    if refresh_token:
        await repository_auth.update_refresh_token(
            username=body.username, refresh_token=refresh_token, db=db
        )
    new_access_token = token.get("access_token")
    if SET_COOKIES:
        if new_access_token:
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                path="/api/",
                expires=token.get("expire_access_token"),
            )
        else:
            response.delete_cookie(key="access_token", httponly=True, path="/api/")
        if new_access_token:
            print(f"{token.get('expire_refresh_token')=}")
            response.set_cookie(
                key="refresh_token",
                value=refresh_token, # type: ignore
                httponly=True,
                path="/api/",
                expires=token.get("expire_refresh_token"),
            )
        else:
            response.delete_cookie(key="refresh_token", httponly=True, path="/api/")
    print("login", token)
    return token


async def get_current_user(
    response: Response,
    access_token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
    token: str | None = Depends(repository_auth.auth_service.auth_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Отримує поточного користувача.

    Args:
        response (Response): Об'єкт відповіді.
        access_token (Annotated[str | None, Cookie()]): Токен доступу.
        refresh_token (Annotated[str | None, Cookie()]): Токен оновлення.
        token (str | None): Токен доступу.
        db (Session): Сесія бази даних.

    Returns:
        User | None: Поточний користувач або None, якщо користувач не авторизований.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer",
            "set-cookie": response.headers.get("set-cookie", ""),
        },
    )
    user = None
    new_access_token = None
    print(f"{access_token=}, {refresh_token=}, {token=}")
    if not token:
        print("used cookie access_token")
        token = access_token
    if token:
        user = await repository_auth.a_get_current_user(token, db)
        if not user and token != access_token:
            user = await repository_auth.a_get_current_user(access_token, db)
        if not user and refresh_token:
            result = await refresh_access_token(refresh_token)
            print(f"refresh_access_token  {result=}")
            if result:
                new_access_token = result.get("access_token")
                email = result.get("email")
                user = await repository_users.get_user_by_email(str(email), db)
                if SET_COOKIES:
                    if new_access_token:
                        response.set_cookie(
                            key="access_token",
                            value=new_access_token,
                            httponly=True,
                            path="/api/",
                            expires=result.get("expire_token"),
                        )
                    else:
                        response.delete_cookie(
                            key="access_token", httponly=True, path="/api/"
                        )
    if user is None:
        raise credentials_exception
    return user


async def get_current_user_dbtoken(
    response: Response,
    access_token: Annotated[str | None, Cookie()] = None,
    refresh_token: Annotated[str | None, Cookie()] = None,
    token: str | None = Depends(repository_auth.auth_service.auth_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """
    Отримує поточного користувача з токеном з бази даних.

    Args:
        response (Response): Об'єкт відповіді.
        access_token (Annotated[str | None, Cookie()]): Токен доступу.
        refresh_token (Annotated[str | None, Cookie()]): Токен оновлення.
        token (str | None): Токен доступу.
        db (Session): Сесія бази даних.

    Returns:
        User | None: Поточний користувач або None, якщо користувач не авторизований.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer",
            "set-cookie": response.headers["set-cookie"],
        },
    )
    user = None
    new_access_token = None
    print(f"{access_token=}, {refresh_token=}")
    if not token:
        token = access_token
    if token:
        user = await repository_auth.a_get_current_user(token, db)
        if not user and refresh_token:
            email = await repository_auth.auth_service.decode_refresh_token(
                refresh_token
            )
            user = await repository_users.get_user_by_email(str(email), db)
            # print(f"refresh_access_token {email=} {user.email} {user.refresh_token}")  # type: ignore
            if refresh_token == user.refresh_token:  # type: ignore
                result = await refresh_access_token(refresh_token)
                print(f"refresh_access_token  {result=}")
                if result:
                    new_access_token = result.get("access_token")
                    email = result.get("email")
                    user = await repository_users.get_user_by_email(str(email), db)
                    if SET_COOKIES:
                        if new_access_token:
                            response.set_cookie(
                                key="access_token",
                                value=new_access_token,
                                httponly=True,
                                path="/api/",
                                expires=result.get("expire_token"),
                            )
                        else:
                            response.delete_cookie(
                                key="access_token", httponly=True, path="/api/"
                            )
            else:
                await repository_users.update_user_refresh_token(user, "", db)
                response.delete_cookie(key="refresh_token", httponly=True, path="/api/")
                user = None
    if user is None:
        raise credentials_exception
    return user


@router.get("/secret")
async def read_item(current_user: User = Depends(get_current_user)):
    """
    Отримує доступ до секретної сторінки для авторизованих користувачів.

    Args:
        current_user (User): Поточний користувач.

    Returns:
        dict: Дані доступу до секретної сторінки.
    """
    auth_result = {"email": current_user.email}
    return {"message": "secret router", "owner": auth_result}


@router.get("/secret_dbtoken")
async def read_item_dbtoken(current_user: User = Depends(get_current_user_dbtoken)):
    """
    Отримує доступ до секретної сторінки для авторизованих користувачів з токеном з бази даних.

    Args:
        current_user (User): Поточний користувач.

    Returns:
        dict: Дані доступу до секретної сторінки.
    """
    auth_result = {"email": current_user.email}
    return {"message": "secret router", "owner": auth_result}


async def refresh_access_token(refresh_token: str) -> dict[str, Any] | None:
    """
    Оновлює токен доступу на основі токену оновлення.

    Args:
        refresh_token (str): Токен оновлення.

    Returns:
        dict[str, Any] | None: Нові дані токена доступу або None, якщо оновлення не вдалося.
    """
    if refresh_token:
        email = await repository_auth.auth_service.decode_refresh_token(refresh_token)
        if email:
            (
                access_token,
                expire_token,
            ) = await repository_auth.auth_service.create_access_token(
                data={"sub": email}
            )
            return {
                "access_token": access_token,
                "expire_token": expire_token,
                "email": email,
            }
    return None


@router.get("/refresh_token")
async def refresh_token(
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """
    Оновлює токен доступу на основі токену оновлення.

    Args:
        response (Response): Об'єкт відповіді.
        refresh_token (Annotated[str | None, Cookie()]): Токен оновлення.
        credentials (HTTPAuthorizationCredentials): Об'єкт авторизації.
        db (Session): Сесія бази даних.

    Returns:
        dict: Нові дані токена доступу.
    """
    token: str = credentials.credentials
    print(f"refresh_token {token=}")
    if not token and refresh_token:
        token = refresh_token
    email = await repository_auth.auth_service.decode_refresh_token(token)
    print(f"refresh_token {email=}")
    user: User | None = await repository_users.get_user_by_email(email, db)
    if user and user.refresh_token != token:  # type: ignore
        await repository_users.update_user_refresh_token(user, None, db)
        response.delete_cookie(key="refresh_token", httponly=True, path="/api/")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={
                "set-cookie": response.headers.get("set-cookie", ""),
            },
        )

    (
        new_access_token,
        expire_access_token,
    ) = await repository_auth.auth_service.create_access_token(data={"sub": email})
    (
        new_refresh_token,
        expire_refresh_token,
    ) = await repository_auth.auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_user_refresh_token(user, new_refresh_token, db)
    if SET_COOKIES:
        if new_access_token:
            response.set_cookie(
                key="access_token",
                value=new_access_token,
                httponly=True,
                path="/api/",
                expires=expire_access_token,
            )
        else:
            response.delete_cookie(key="access_token", httponly=True, path="/api/")
        if new_access_token:
            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                httponly=True,
                path="/api/",
                expires=expire_refresh_token,
            )
        else:
            response.delete_cookie(key="refresh_token", httponly=True, path="/api/")
    return {
        "access_token": new_access_token,
        "expire_access_token": expire_access_token,
        "refresh_token": new_refresh_token,
        "expire_refresh_token": expire_refresh_token,
        "token_type": "bearer",
    }
