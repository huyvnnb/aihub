from uuid import UUID

from fastapi import Depends
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_db
from app.db.models import Role
from app.db.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)

    async def get_role_by_name(self, name: str):
        statement = select(Role).where(Role.name == name)
        role = await self.session.execute(statement)
        return role.scalars().first()



# def get_role_repo(db: Session = Depends(get_db)) -> RoleRepository:
#     return RoleRepository(db=db)