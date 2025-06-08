from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models import Permission
from app.db.repositories.base_repository import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    def __init__(self, session: AsyncSession):
        super().__init__(Permission, session)

    async def get_perm_by_name(self, name: str):
        stmt = select(Permission).where(Permission.name == name)
        result = await self.session.execute(stmt)
        return result.first()