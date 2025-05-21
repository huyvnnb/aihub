from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship
from pydantic import EmailStr


# from app.db.models.rftoken_model import RFToken
from app.db.models.base_model import CoreModel
from ...utils.enums import Gender

# from app.db.models.role_model import Role

if TYPE_CHECKING:
    from .rftoken_model import RFToken
    from .role_model import Role


class User(CoreModel, table=True):
    __tablename__ = 'users'

    email: EmailStr = Field(unique=True, index=True, max_length=255, nullable=False)
    password_hash: str = Field(nullable=False, max_length=255)
    fullname: str = Field(nullable=False, max_length=50)
    dob: date = Field(nullable=False)
    address: Optional[str] = Field(default=None, max_length=255)
    gender: Gender = Field(nullable=False)
    avatar: str = Field(default="")
    verified: bool = Field(default=False, nullable=False)
    verify_token: str = Field(nullable=True, default=None)
    verify_token_expire: Optional[datetime] = Field(default=None)
    role_id: UUID = Field(foreign_key="roles.id", nullable=False)

    role: Optional["Role"] = Relationship(back_populates="users")
    refresh_tokens: List["RFToken"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})



