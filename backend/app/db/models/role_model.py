from typing import List, Optional, TYPE_CHECKING

from app.db.models.base_model import CoreModel, DeletedModel
from sqlmodel import Field, Relationship
# from app.db.models.user_model import User
# from app.db.models.permission_model import Permission, RolePermission
from app.db.models.permission_model import RolePermission, DeletedPermission

if TYPE_CHECKING:
    from .user_model import User, DeletedUser
    from .permission_model import Permission


class Role(CoreModel, table=True):
    __tablename__ = 'roles'

    name: str = Field(nullable=False, max_length=50, index=True, unique=True)
    desc: Optional[str] = Field(default=None, nullable=True)

    users: List["User"] = Relationship(back_populates="role")
    permissions: List["Permission"] = Relationship(back_populates="roles", link_model=RolePermission)


class DeletedRole(DeletedModel, table=True):
    __tablename__ = 'deleted_roles'

    name: str = Field(max_length=50, index=True)
    desc: Optional[str] = Field(nullable=True)

