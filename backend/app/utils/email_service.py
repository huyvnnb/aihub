import asyncio
import functools
from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from app.core.config import settings

from app.core.config import settings
from app.utils.enums import EmailType

BASE_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = BASE_DIR / "email-templates"

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=str(TEMPLATE_DIR)
)

fm = FastMail(conf)


async def send_email(
        recipient_email: EmailStr,
        subject: str,
        template_name: EmailType,
        context: dict
):
    message = MessageSchema(
        subject=subject,
        recipients=[recipient_email],
        template_body=context,
        subtype=MessageType.html
    )
    try:
        await fm.send_message(message, template_name=f"{template_name}.html")
    except Exception as e:
        print(f"Error sending email: {e}")

