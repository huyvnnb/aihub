from fastapi import Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.core.exceptions import NotFoundError
from app.db.models import Role
from app.db.repositories.role_repository import RoleRepository
from app.schemas.role_schema import RoleCreate, RoleResponse
from app.utils import messages


class RoleService:
    def __init__(self, session: AsyncSession):
        self.role_repo = RoleRepository(session)

    async def create_role(self, role_in: RoleCreate) -> RoleResponse:
        existing_role = await self.role_repo.get_role_by_name(role_in.name)
        if existing_role:
            raise NotFoundError(messages.Role.ROLE_NOT_FOUND)

        role = Role(**role_in.model_dump())
        await self.role_repo.create(role)

        return RoleResponse.model_validate(role)