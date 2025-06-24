from app.utils.enums import Role
from enum import Enum


DEFAULT_ROLE = Role.USER


class P(str, Enum):
    """
    Enum chứa các hằng số định danh cho các quyền (Permissions) trong hệ thống.
    Viết tắt là `P` để ngắn gọn và tránh xung đột tên với model `Permission`.
    """
    # === Items ===
    ITEM_READ = "item:read"
    ITEM_CREATE = "item:create"
    ITEM_UPDATE = "item:update"
    ITEM_DELETE = "item:delete"

    # === Users ===
    USER_CREATE = "user:create"
    USER_CREATE_LIST = "user:create_list"
    USER_READ_LIST = "user:read_list"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_UPDATE_SELF = "user:update_self"

    # === Roles & Permissions (Admin level) ===
    ROLES_MANAGE = "roles:manage"  # Quản lý roles (tạo, sửa, xóa)
    PERMISSIONS_ASSIGN = "permissions:assign"  # Gán quyền cho roles

    @classmethod
    def all(cls) -> list[str]:
        """Trả về một list chứa tất cả các giá trị chuỗi của quyền."""
        return [item.value for item in cls]
