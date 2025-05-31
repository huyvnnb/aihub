import secrets
import string
import uuid
from datetime import timedelta, datetime, timezone

import jwt
from jwt import InvalidTokenError

from app.core import security
from app.core.config import settings


def generate_jwt_token(user_id: uuid.UUID, expires_in: int) -> str:
    delta = timedelta(seconds=expires_in)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()

    payload = {
        "exp": expires.timestamp(),
        "iat": now.timestamp(),
        "sub": str(user_id)
    }\

    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt


def verify_jwt_token(token: str, leeway_seconds: int = 0) -> str | None:
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM],
            leeway=timedelta(seconds=leeway_seconds)
        )
        return str(decoded_token["sub"])
    except InvalidTokenError:
        return None


def generate_token(length: int = 8) -> str:
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

