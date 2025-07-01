from functools import partial
from typing import Any

from app.utils import messages


class ApplicationError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)
    # @property
    # def message(self):
    #     return self.args[0]


class InvalidTokenError(ApplicationError):
    def __init__(self, message: str):
        super().__init__(message)


class SystemConfigError(ApplicationError):
    def __init__(self, message: str):
        super().__init__(message)


class DuplicateEntryError(ApplicationError):
    def __init__(self, message: str):
        super().__init__(message)


class NotFoundError(ApplicationError):
    def __init__(self, message: messages):
        super().__init__(message)


# UserNotFound = partial(NotFoundError, entity_name="user")
# RoleNotFound = partial(NotFoundError, entity_name="role")
# PermissionNotFound = partial(NotFoundError, entity_name="permission")
#
# DuplicateUser = partial(DuplicateEntryError, entity_name="USER")
# DuplicateRole = partial(DuplicateEntryError, entity_name="role")
# DuplicatePermission = partial(DuplicateEntryError, entity_name="permission")


