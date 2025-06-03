import secrets
import string
import uuid
from datetime import timedelta, datetime, timezone

import jwt
from jwt import InvalidTokenError, ExpiredSignatureError, DecodeError

from app.core import security
from app.core.config import settings
from app.utils.enums import Module
from app.utils.logger import get_logger

logger = get_logger(Module.TOKEN_UTIL)


def generate_jwt_token(user_id: uuid.UUID, expires_in: int) -> str:
    delta = timedelta(seconds=expires_in)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()

    payload = {
        "exp": expires.timestamp(),
        "iat": now.timestamp(),
        "sub": str(user_id)
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt


def verify_jwt_token(token: str, private_key: str, leeway_seconds: int = 0) -> str | None:
    try:
        decoded_token = jwt.decode(
            token,
            private_key,
            algorithms=[security.ALGORITHM],
            leeway=timedelta(seconds=leeway_seconds)
        )
        return str(decoded_token["sub"])

    except ExpiredSignatureError:
        logger.error("Token expired")
    except DecodeError:
        logger.error("Token is invalid")
    except InvalidTokenError:
        logger.error("Invalid token")


def generate_token(length: int = 8) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

