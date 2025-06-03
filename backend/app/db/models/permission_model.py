from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from sqlmodel import SQLModel, Relationship, Field
from app.db.models.base_model import CoreModel
# from app.db.models.role_model import Role

if TYPE_CHECKING:
    from .role_model import Role


class RolePermission(SQLModel, table=True):
    __tablename__ = "role_permission"

    role_id: int = Field(foreign_key="roles.id", primary_key=True, nullable=False)
    permission_id: int = Field(foreign_key="permissions.id", primary_key=True, nullable=False)


class Permission(CoreModel, table=True):
    __tablename__ = 'permissions'

    name: str = Field(nullable=False, unique=True)
    display_name: Optional[str] = Field(default=None, max_length=100)
    desc: Optional[str] = Field(default=None, nullable=True)
    module: Optional[str] = Field(default=None, nullable=False, max_length=50)

    roles: List["Role"] = Relationship(back_populates="permissions", link_model=RolePermission)


