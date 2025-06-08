from uuid import UUID

from fastapi import Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.db.repositories.role_repository import RoleRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserResponse


class UserService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)
