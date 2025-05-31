import logging
import sys
from enum import Enum

RESET = "\x1b[0m"
GREEN = "\x1b[32m"  # Màu cho thời gian
BLUE = "\x1b[34m"
YELLOW = "\x1b[33m"
RED = "\x1b[31m"
BOLD = "\x1b[1m"


class Module(Enum):
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


class UvicornLikeFormatter(logging.Formatter):
    LEVEL_COLOR = {
        "INFO": GREEN,  # Có thể bạn muốn màu khác cho INFO level text
        "DEBUG": BLUE,
        "WARNING": YELLOW,
        "ERROR": RED,
        "CRITICAL": RED,
    }

    def format(self, record):
        original_levelname = record.levelname
        level_color = self.LEVEL_COLOR.get(original_levelname, RESET)

        record.levelname = f"{BOLD}{level_color}{original_levelname + ':':<9}{RESET}"

        formatted_time = self.formatTime(record, self.datefmt)
        record.asctime = f"{BOLD}{GREEN}{formatted_time}{RESET}"

        log_message = super().format(record)
        record.levelname = original_levelname

        return log_message


LOG_FORMAT = "%(levelname)s %(asctime)s - [%(name)s] - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def get_logger(name: str | Enum = "uvicorn", level: int = logging.DEBUG) -> logging.Logger:
    if isinstance(name, Enum):
        name = name.value

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.hasHandlers(): # Chỉ thêm handler nếu logger chưa có
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level) # Handler cũng cần level
        formatter = UvicornLikeFormatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False # Thường là tốt khi bạn có handler tùy chỉnh

    return logger


if __name__ == '__main__':
    logger = get_logger(level=logging.DEBUG)
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    logger.critical("This is a CRITICAL message")

    print("\n--- Example with a different logger (INFO level) ---")
    info_logger = get_logger("my_app", level=logging.INFO)
    info_logger.debug("This DEBUG from my_app will NOT show.")
    info_logger.info("This INFO from my_app WILL show.")

    print("\n--- Re-getting the first logger (should not add new handler) ---")
    same_logger = get_logger()
    print(f"Number of handlers for 'uvicorn' logger: {len(same_logger.handlers)}")
    same_logger.error("Another INFO from 'uvicorn' logger.")