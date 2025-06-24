import logging
from typing import Optional

from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.models import User, Role
from app.db.repositories.base_repository import BaseRepository
from app.utils.logger import get_logger, Module

logger = get_logger(Module.USER_REPO)


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)

    async def get_user_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(
            User.email == email, User.deleted == False
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
        count_stmt = select(func.count()).select_from(User).where(User.deleted.is_(False))

        user_result = await self.session.execute(statement)
        count_result = await self.session.execute(count_stmt)

        users = user_result.all()
        total_items = count_result.scalar_one()

        return users, total_items


# def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
#     return UserRepository(session=db)
