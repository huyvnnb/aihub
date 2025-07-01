from typing import List
from uuid import UUID

from fastapi import Depends
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models import Role
from app.db.repositories.base_repository import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(self, session: AsyncSession):
        super().__init__(Role, session)

    async def get_role_by_name(self, name: str):
        statement = select(Role).where(Role.name == name)
        role = await self.session.execute(statement)
        return role.scalars().first()

    async def get_roles_by_names(self, names: List[str]) -> List[Role]:
        if not names:
            return []

        stm = select(Role).where(Role.name.in_(names))
        result = await self.session.execute(stm)

        return result.scalars().all()



# def get_role_repo(db: Session = Depends(get_db)) -> RoleRepository:
#     return RoleRepository(db=db)