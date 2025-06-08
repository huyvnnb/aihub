from fastapi import Depends
from sqlmodel import Session
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import get_db
from app.db.models import RFToken
from app.db.repositories.base_repository import BaseRepository


class RFTokenRepository(BaseRepository[RFToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RFToken, session)



