from fastapi import HTTPException
from sqlalchemy.orm import selectinload, undefer
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.core.exceptions import NotFoundError, DuplicateEntryError
from app.db.models import Permission
from app.db.repositories.permission_repository import PermissionRepository
from app.schemas.perm_schema import PermCreate, PermResponse
from app.services.unit_of_work import UnitOfWork
from app.utils import messages


# class PermissionService:
#     def __init__(self, session: AsyncSession):
#         self.perm_repo = PermissionRepository(session)
#
#     async def create_perm(self, perm_in: PermCreate):
#         existing_perm = await self.perm_repo.get_perm_by_name(perm_in.name)
#         if existing_perm:
#             raise DuplicateEntryError(messages.Permission.PERMISSION_ALREADY_EXISTS)
#
#         perm = Permission(**perm_in.model_dump())
#         await self.perm_repo.create(perm)
#
#     async def get_perm_by_id(self, perm_id: int):
#         existing_perm = await self.perm_repo.get_by_id(perm_id)
#         if not existing_perm:
#             raise NotFoundError(messages.Permission.PERMISSION_NOT_FOUND)
#
#         response = PermResponse.model_validate(existing_perm)
#         return response

class PermissionService:
    async def create_perm(self, uow: UnitOfWork, perm_in: PermCreate):
        async with uow:
            perm_repo = uow.permissions
            existing_perm = await perm_repo.get_perm_by_name(perm_in.name)
            if existing_perm:
                raise DuplicateEntryError(messages.Permission.PERMISSION_ALREADY_EXISTS)

            perm = Permission(**perm_in.model_dump())
            await perm_repo.create(perm)

    async def get_perm_by_id(self, uow: UnitOfWork, perm_id: int):
        load_options = [
            selectinload(Permission.roles)
        ]
        async with uow:
            perm_repo = uow.permissions
            existing_perm = await perm_repo.get_by_id(perm_id, load_options=load_options)
            if not existing_perm:
                raise NotFoundError(messages.Permission.PERMISSION_NOT_FOUND)

        response = PermResponse.model_validate(existing_perm)
        return response


def get_perm_service():
    return PermissionService()
