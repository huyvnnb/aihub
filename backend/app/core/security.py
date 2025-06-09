import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=11)

ALGORITHM = "HS256"


def _create_access_token_sync(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def _verify_password_sync(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def _get_password_hash_sync(password: str) -> str:
    return pwd_context.hash(password)


def _get_token_hash_sync(token: str) -> str:
    return pwd_context.hash(token)


def _verify_token_sync(plain_token: str, hashed_token: str) -> bool:
    return pwd_context.verify(plain_token, hashed_token)


# Async version
# def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
#     expire = datetime.now(timezone.utc) + expires_delta
#     to_encode = {"exp": expire, "sub": str(subject)}
#     encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        _verify_password_sync,
        plain_password,
        hashed_password
    )


async def get_password_hash(password: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        _get_password_hash_sync,
        password
    )


async def get_token_hash(token: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        _get_token_hash_sync,
        token
    )


async def verify_token(plain_token: str, hashed_token: str) -> bool:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None, _verify_token_sync, plain_token, hashed_token
    )
