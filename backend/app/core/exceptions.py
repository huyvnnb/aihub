from typing import Any

from app.utils import messages


class ApplicationError(Exception):
    @property
    def message(self):
        return self.args[0]


class DuplicateEntryError(ApplicationError):
    def __init__(self, entity_name: str):
        message = messages.ErrorMessages.DUPLICATE_ENTRY.format(entity_name=entity_name)
        super().__init__(message)
        self.entity_name = entity_name


class NotFoundError(ApplicationError):
    def __init__(self, entity_name: str, entity_id: Any):
        message = messages.ErrorMessages.ENTRY_NOT_FOUND.format(entity_id=entity_id, entity_name=entity_name)
        super().__init__(message)
        self.entity_name=entity_name
        self.entity_id=entity_id



