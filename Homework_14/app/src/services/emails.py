import logging
from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr, BaseModel


from ..conf.config import settings
from ..services.auth.auth import auth_service

logger = logging.getLogger(f"{settings.app_name}.{__name__}")

class EmailSchema(BaseModel):
    """Class EmailSchema

    :param BaseModel: _description_
    :type BaseModel: _type_
    """
    email: EmailStr
    fullname: str = "Sender Name"
    subject: str = "Sender Subject topic"


async def send_email(email: str, username: str, host: str):
    """Service email send_email

    :param email: _description_
    :type email: str
    :param username: _description_
    :type username: str
    :param host: _description_
    :type host: str
    :return: _description_
    :rtype: _type_
    """
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "token": token_verification,
                "host": host,
                "username": username,
            },
            subtype=MessageType.html,
        )
        logger.debug(message)

        fm = FastMail(conf)
        await fm.send_message(message, template_name="confirm_email.html")
    except ConnectionError as err:
        logger.error(err)
        return None
    return {"message": "email has been set to sending query"}


conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)