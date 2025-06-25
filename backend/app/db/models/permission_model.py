from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, func
from sqlmodel import SQLModel, Relationship, Field
from app.db.models.base_model import CoreModel, DeletedModel

# from app.db.models.role_model import Role

if TYPE_CHECKING:
    from .role_model import Role, DeletedRole


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


class DeletedPermission(DeletedModel, table=True):
    __tablename__ = 'deleted_permissions'

    name: str = Field(nullable=False, index=True)
    display_name: Optional[str] = Field(max_length=100)
    desc: Optional[str]
    module: Optional[str] = Field(max_length=50)


class DeletedRolePermission(SQLModel, table=True):
    __tablename__ = 'deleted_role_permission'

    id: Optional[int] = Field(default=None, primary_key=True)
    original_role_id: int = Field(index=True, nullable=False)
    original_permission_id: int = Field(index=True, nullable=False)

    archived_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": func.now(),
            "nullable": False,
        }
    )


