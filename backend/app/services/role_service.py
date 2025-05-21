from fastapi import Depends, HTTPException
from starlette import status

from app.db.models import Role
from app.db.repositories.role_repository import RoleRepository, get_role_repo
from app.schemas.role_schema import RoleCreate


class RoleService:
    def __init__(self, role_repo: RoleRepository = Depends(get_role_repo)):
        self.role_repo = role_repo

    def create_role(self, role_in: RoleCreate):
        existing_role = self.role_repo.get_role_by_name(role_in.name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name already existed"
            )
        role = Role(**role_in.model_dump())
        self.role_repo.create_role(role)