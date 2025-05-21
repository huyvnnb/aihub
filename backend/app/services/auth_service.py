from fastapi import Depends, HTTPException, status

from app.core.security import get_password_hash
from app.db.models import User
from app.db.repositories.role_repository import RoleRepository, get_role_repo
from app.db.repositories.user_repository import UserRepository, get_user_repo
from app.schemas.user_schema import UserCreate
from app.utils.constants import DEFAULT_ROLE


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository = Depends(get_user_repo),
        role_repo: RoleRepository = Depends(get_role_repo)
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo

    def register(self, user_in: UserCreate):
        existing_user = self.user_repo.get_user_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already existed"
            )
        user_data = user_in.model_dump(exclude={"password"})
        password_hash = get_password_hash(user_in.password)
        existing_role = self.role_repo.get_role_by_name(DEFAULT_ROLE)
        if not existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role {DEFAULT_ROLE} not exist"
            )
        user = User(
            **user_data,
            password_hash=password_hash,
            role_id=existing_role.id
        )
        return self.user_repo.create(user)

