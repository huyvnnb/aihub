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
