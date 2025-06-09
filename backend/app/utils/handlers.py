# file: app/core/error_handlers.py

import logging
import traceback

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Import các exception và schema của bạn
from app.core.exceptions import (
    ApplicationError,
    DuplicateEntryError,
    NotFoundError,
)
from app.schemas.response_schema import ErrorDetail, ErrorResponse, ModelResponse
from app.utils import messages
from app.utils.enums import Module
from app.utils.logger import get_logger

logger = get_logger(Module.EXCEPTION)


# --- HANDLER CHO CÁC LỖI TÙY CHỈNH (CUSTOM EXCEPTIONS) ---

def _create_error_json_response(status_code: int, code: str, message: str, details: list[ErrorDetail] | None = None) -> JSONResponse:
    error_response = ModelResponse(
        success=False,
        error=ErrorResponse(code=code, details=details)
    )
    return JSONResponse(
        status_code=status_code,
        content=error_response.model_dump(exclude_none=True)
    )


async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return _create_error_json_response(
        status_code=status.HTTP_404_NOT_FOUND,
        code="HTTP_404_NOT_FOUND",
        message=exc.message,
        details=[
            ErrorDetail(
                msg=exc.message,
                type="not_found_error",
            )
        ]
    )


async def duplicate_entry_error_handler(
    request: Request, exc: DuplicateEntryError
) -> JSONResponse:
    """Xử lý lỗi DuplicateEntryError tùy chỉnh, trả về 409."""
    return _create_error_json_response(
        status_code=status.HTTP_409_CONFLICT,
        code="HTTP_409_CONFLICT",
        message=exc.message,
        details=[
            ErrorDetail(
                msg=exc.message,
                type="duplicate_entry_error",
            )
        ]
    )


async def application_error_handler(
    request: Request, exc: ApplicationError
) -> JSONResponse:
    """Xử lý các lỗi ApplicationError chung khác, trả về 400."""
    return _create_error_json_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        code="HTTP_400_BAD_REQUEST",
        message=exc.message,
        details=[
            ErrorDetail(
                loc=["application"], msg=exc.message, type="application_error"
            )
        ]
    )


# --- HANDLER CHO CÁC LỖI CƠ SỞ DỮ LIỆU (DATABASE ERRORS) ---

async def integrity_error_handler(
    request: Request, exc: IntegrityError
) -> JSONResponse:
    """Xử lý lỗi IntegrityError, trả về 400 (thường do vi phạm ràng buộc)."""
    logger.warning(f"IntegrityError on request {request.url.path}: {exc}")
    return _create_error_json_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        code="HTTP_400_BAD_REQUEST",
        message=messages.DatabaseError.INTEGRITY_ERROR,
        details=[
            ErrorDetail(
                loc=["database", "integrity"],
                msg=str(exc.orig),
                type="integrity_error",
            )
        ]
    )


async def sqlalchemy_error_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Xử lý các lỗi SQLAlchemy chung khác, trả về 503 (Dịch vụ không sẵn sàng)."""
    logger.error(f"SQLAlchemyError on request {request.url.path}: {exc}")
    logger.error(traceback.format_exc())
    return _create_error_json_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        code="HTTP_503_SERVICE_UNAVAILABLE",
        message="Đã có lỗi xảy ra với hệ thống cơ sở dữ liệu. Vui lòng thử lại sau.",
        details=None
    )


# --- HANDLER CHO CÁC LỖI HTTP VÀ VALIDATION CỦA FASTAPI ---

async def http_exception_handler(
    request: Request, exc: HTTPException
) -> JSONResponse:
    """Xử lý các lỗi HTTPException của FastAPI."""
    response = _create_error_json_response(
        status_code=exc.status_code,
        code=f"HTTP_{exc.status_code}",
        message=str(exc.detail),
        details=[
            ErrorDetail(
                loc=["http"], msg=str(exc.detail), type="http_exception"
            )
        ]
    )
    if exc.headers:
        response.headers.update(exc.headers)
    return response


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Xử lý lỗi validation của Pydantic, trả về 422."""
    details = []
    for error in exc.errors():
        details.append(
            ErrorDetail(
                loc=list(map(str, error["loc"])), msg=error["msg"], type=error["type"]
            )
        )

    return _create_error_json_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        code="HTTP_422_UNPROCESSABLE_ENTITY",
        message="Dữ liệu không hợp lệ.",
        details=details
    )


# --- HANDLER BẮT TẤT CẢ (CATCH-ALL) ---

async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Xử lý tất cả các lỗi không được xử lý khác, trả về 500."""
    logger.error(f"Unhandled exception for request {request.url.path}: {exc}")
    logger.error(traceback.format_exc())
    return _create_error_json_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="HTTP_500_INTERNAL_SERVER_ERROR",
        message="Đã xảy ra lỗi hệ thống không mong muốn. Vui lòng liên hệ quản trị viên.",
        details=None
    )