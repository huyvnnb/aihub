import logging
from typing import Optional

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models import User, Role
from app.db.models.user_model import DeletedUser
from app.db.repositories.base_repository import BaseRepository
from app.utils.logger import get_logger, Module

logger = get_logger(Module.USER_REPO)


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(
            User.email == email
        )
        user = await self.session.execute(statement)
        return user.scalars().first()

    async def get_all_users(self, offset: int, size: int):
        statement = (
            select(User, Role.name.label("role"))
            .join(Role, User.role_id == Role.id)
            .order_by(User.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        count_stmt = select(func.count()).select_from(User)

        user_result = await self.session.exec(statement)
        count_result = await self.session.exec(count_stmt)

        users = user_result.all()
        total_items = count_result.one_or_none()

        return users, total_items

    async def get_user_by_token(self, token: str) -> User:
        statement = select(User).where(User.verify_token == token)
        user = await self.session.execute(statement)

        return user.scalar_one_or_none()


class DeletedUserRepository(BaseRepository[DeletedUser]):
    def __init__(self, session: AsyncSession):
        super().__init__(DeletedUser, session)

# def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
#     return UserRepository(session=db)
