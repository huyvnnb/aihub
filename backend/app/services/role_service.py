from fastapi import Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.core.exceptions import NotFoundError
from app.db.models import Role
from app.db.repositories.role_repository import RoleRepository
from app.schemas.role_schema import RoleCreate, RoleResponse
from app.services.unit_of_work import UnitOfWork
from app.utils import messages


class RoleService:

    async def create_role(self, uow: UnitOfWork, role_in: RoleCreate) -> RoleResponse:
        async with uow:
            existing_role = await uow.roles.get_role_by_name(role_in.name)
            if existing_role:
                raise NotFoundError(messages.Role.ROLE_NOT_FOUND)

            role = Role(**role_in.model_dump())
            await uow.roles.create(role)

        return RoleResponse.model_validate(role)


def get_role_service():
    return RoleService()
