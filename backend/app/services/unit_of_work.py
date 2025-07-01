from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.repositories.permission_repository import PermissionRepository
from app.db.repositories.rftoken_repository import RFTokenRepository
from app.db.repositories.role_repository import RoleRepository
from app.db.repositories.user_repository import UserRepository


class UnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    @property
    def users(self) -> UserRepository:
        if not hasattr(self, '_users'):
            self._users = UserRepository(self.session)

        return self._users

    @property
    def roles(self) -> RoleRepository:
        if not hasattr(self, '_roles'):
            self._roles = RoleRepository(self.session)

        return self._roles

    @property
    def permissions(self) -> PermissionRepository:
        if not hasattr(self, '_perms'):
            self._perms = PermissionRepository(self.session)

        return self._perms

    @property
    def rftoken(self) -> RFTokenRepository:
        if not hasattr(self, '_rftoken'):
            self._rftoken = RFTokenRepository(self.session)

        return self._rftoken

