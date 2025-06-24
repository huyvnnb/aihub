from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.db import engine, get_session
from app.core.exceptions import NotFoundError
from app.db.models import User
from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.token_schema import TokenPayload
from app.utils import messages

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_session)]


async def get_current_user(session: AsyncSessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user_repo = UserRepository(session)
    user = await user_repo.get_by_id(token_data.sub)
    if not user:
        raise NotFoundError(message=messages.User.USER_NOT_FOUND)
    if not user.verified:
        raise HTTPException(status_code=400, detail=messages.Auth.ACCOUNT_NOT_YET_ACTIVE)
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]


def require_permission(perm_name: str):
    async def wrapper(user: CurrentUser, session: AsyncSessionDep):
        perm_repo = PermissionRepository(session)
        existing_perm = await perm_repo.get_perm_by_role(user.role_id, perm_name)

        if not existing_perm:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=messages.Auth.PERMISSION_DENIED
            )

    return wrapper
#
#
# def get_current_active_superuser(current_user: CurrentUser) -> User:
#     if not current_user.is_superuser:
#         raise HTTPException(
#             status_code=403, detail="The user doesn't have enough privileges"
#         )
#     return current_user
