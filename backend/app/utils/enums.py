from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"


class EmailType(str, Enum):
    VERIFY_ACCOUNT = "verify_account"
    RESET_PASSWORD = "reset_password"


class Module(str, Enum):
    APP = "APPLICATION"

    # User
    USER_REPO = "USER_REPO"
    USER_SERVICE = "USER_SERVICE"
    USER_ROUTER = "USER_ROUTER"

    # Admin
    ADMIN_SERVICE = "ADMIN_SERVICE"
    ADMIN_ROUTER = "ADMIN_ROUTER"

    # Role
    ROLE_REPO = "ROLE_REPO"
    ROLE_SERVICE = "ROLE_SERVICE"
    ROLE_ROUTER = "ROLE_ROUTER"

    # Util
    TOKEN_UTIL = "TOKEN"
