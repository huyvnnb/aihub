from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"


class Role(str, Enum):
    USER = "user"
    ADMIN = "admin"
