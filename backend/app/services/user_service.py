from uuid import UUID

from fastapi import Depends, HTTPException
from starlette import status

from app.db.repositories.role_repository import RoleRepository, get_role_repo
from app.db.repositories.user_repository import UserRepository, get_user_repo
from app.schemas.user_schema import UserResponse


class UserService:
    def __init__(self,
                 user_repo: UserRepository = Depends(get_user_repo),
                 role_repo: RoleRepository = Depends(get_role_repo)
                 ):
        self.user_repo = user_repo
        self.role_repo = role_repo
