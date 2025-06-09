import asyncio
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
from fastapi import Request

logger = get_logger(Module.TOKEN_UTIL)


def _generate_jwt_token_sync(user_id: uuid.UUID, expires_in: int) -> str:
    delta = timedelta(seconds=expires_in)
    now = datetime.now(timezone.utc)
    expires = now + delta

    payload = {
        "exp": expires,  # pyjwt khuyến nghị dùng trực tiếp datetime object
        "iat": now,
        "sub": str(user_id)
    }
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )


def _verify_jwt_token_sync(token: str, private_key: str, leeway_seconds: int = 0) -> str | None:
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
        return None
    except DecodeError:
        logger.error("Token is invalid")
        return None
    except InvalidTokenError:
        logger.error("Invalid token")
        return None


def _generate_token_sync(length: int = 8) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


# Async
async def generate_jwt_token(user_id: uuid.UUID, expires_in: int) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        _generate_jwt_token_sync,
        user_id,
        expires_in
    )


async def verify_jwt_token(token: str, private_key: str, leeway_seconds: int = 0) -> str | None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        _verify_jwt_token_sync,
        token,
        private_key,
        leeway_seconds
    )


async def generate_token(length: int = 8) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        _generate_token_sync,
        length
    )


def get_client_meta(request: Request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    ip = x_forwarded_for.split(",")[0].strip() if x_forwarded_for else request.client.host

    user_agent = request.headers.get("User-Agent")

    return ip, user_agent
