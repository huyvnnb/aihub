from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship
from pydantic import EmailStr


# from app.db.models.rftoken_model import RFToken
from app.db.models.base_model import CoreModel, DeletedModel
from ...utils.constants import Provider
from ...utils.enums import Gender

# from app.db.models.role_model import Role

if TYPE_CHECKING:
    from .rftoken_model import RFToken
    from .role_model import Role


class User(CoreModel, table=True):

    __tablename__ = 'users'

    id: UUID = Field(primary_key=True, nullable=False, index=True, default_factory=uuid4)
    email: EmailStr = Field(unique=True, index=True, max_length=255, nullable=False)
    password_hash: Optional[str] = Field(nullable=False, max_length=255)
    provider: str = Field(nullable=False, default=Provider.LOCAL)
    provider_id: Optional[str] = Field(default=None)
    fullname: str = Field(nullable=False, max_length=50)
    dob: Optional[date] = Field(default=None)
    address: Optional[str] = Field(default=None, max_length=255)
    gender: Gender = Field(nullable=False)
    avatar: Optional[str] = Field(default=None)
    verified: bool = Field(default=False, nullable=False)
    verify_token: Optional[str] = Field(default=None)
    verify_token_expire: Optional[datetime] = Field(default=None)
    pwd_reset_token: Optional[str] = Field(default=None)
    pwd_reset_expire: Optional[datetime] = Field(default=None)

    role_id: int = Field(foreign_key="roles.id", nullable=False)

    role: Optional["Role"] = Relationship(back_populates="users")
    refresh_tokens: List["RFToken"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class DeletedUser(DeletedModel, table=True):
    __tablename__ = 'deleted_users'

    original_id: UUID = Field(nullable=False, index=True)
    email: EmailStr = Field(index=True, max_length=255, nullable=False)
    password_hash: Optional[str] = Field(max_length=255)
    provider: str = Field(nullable=False)
    provider_id: Optional[str] = Field(default=None)
    fullname: str = Field(max_length=50, nullable=False)
    dob: Optional[date]
    address: Optional[str] = Field(max_length=255)
    gender: Optional[Gender]
    avatar: Optional[str]
    verified: bool
    verify_token: str
    verify_token_expire: Optional[datetime]
    pwd_reset_token: Optional[str]
    pwd_reset_expire: Optional[datetime]
    archived_role_id: int
