from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.core.exceptions import NotFoundError, DuplicateEntryError
from app.db.models import Permission
from app.db.repositories.permission_repository import PermissionRepository
from app.schemas.perm_schema import PermCreate, PermResponse
from app.utils import messages


class PermissionService:
    def __init__(self, session: AsyncSession):
        self.perm_repo = PermissionRepository(session)

    async def create_perm(self, perm_in: PermCreate):
        existing_perm = await self.perm_repo.get_perm_by_name(perm_in.name)
        if existing_perm:
            raise DuplicateEntryError(messages.Permission.PERMISSION_ALREADY_EXISTS)

        perm = Permission(**perm_in.model_dump())
        await self.perm_repo.create(perm)

    async def get_perm_by_id(self, perm_id: int):
        existing_perm = await self.perm_repo.get_by_id(perm_id)
        if not existing_perm:
            raise NotFoundError(messages.Permission.PERMISSION_NOT_FOUND)

        response = PermResponse.model_validate(existing_perm)
        return response
