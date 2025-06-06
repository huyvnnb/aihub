from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models import Permission


class PermissionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, perm: Permission):
        self.session.add(perm)
        await self.session.commit()
        await self.session.refresh(perm)

    async def get_perm_by_id(self, id: int) -> Permission:
        permission = await self.session.get(Permission, id)
        return permission

    async def get_perm_by_name(self, name: str):
        stmt = select(Permission).where(Permission.name == name)
        result = await self.session.execute(stmt)
        return result.first()