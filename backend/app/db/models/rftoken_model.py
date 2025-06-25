from typing import Optional, TYPE_CHECKING, Any

from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel
from uuid import UUID
from datetime import datetime
from app.db.models.base_model import CoreModel
# from app.db.models.user_model import User
from sqlalchemy.dialects.postgresql import INET, TEXT

if TYPE_CHECKING:
    from .user_model import User, DeletedUser


class RFToken(CoreModel, table=True):
    __tablename__ = "refresh_tokens"

    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    token_hash: str = Field(nullable=False, unique=True, index=True, max_length=64)
    expires_at: datetime = Field(nullable=False)
    revoked_at: Optional[datetime] = Field(default=None, nullable=True)
    ip_address: Optional[str] = Field(default=None, nullable=True, sa_type=INET)
    user_agent: Optional[str] = Field(default=None, nullable=True)
    replaced_by: Optional[str] = Field(default=None, nullable=True, max_length=64)
    is_used: bool = Field(default=False, nullable=False)

    user: Optional["User"] = Relationship(
        back_populates="refresh_tokens",
    )
