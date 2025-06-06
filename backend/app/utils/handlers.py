from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette import status
import logging

from app.utils import messages

logger = logging.getLogger(__name__)


from app.schemas.response_schema import ModelResponse, ErrorResponse, ErrorDetail


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    http_exc: HTTPException = exc
    error_response = ModelResponse(
        success=False,
        error=ErrorResponse(
            code=f"HTTP_{http_exc.status_code}",
            message=http_exc.detail if isinstance(http_exc.detail, str) else "Đã xảy ra lỗi",
            details=[
                ErrorDetail(
                    loc=["request", str(request.url)],
                    msg=str(http_exc.detail),
                    type="http_exception"
                )
            ]
        )
    )
    return JSONResponse(
        status_code=http_exc.status_code,
        content=error_response.model_dump(exclude_none=True)
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    error_response = ModelResponse(
        success=False,
        error=ErrorResponse(
            code="HTTP_400_BAD_REQUEST",
            message=messages.DatabaseError.INTEGRITY_ERROR.format(detail=str(exc)),
            details = [
                ErrorDetail(
                    loc=["request", str(request.url)],
                    msg=str(exc),
                    type="http_exception"
                )
            ]
        )
    )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=error_response.model_dump(exclude_none=True)
    )


async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
    error_response = ModelResponse(
        success=False,
        error=ErrorResponse(
            code="HTTP_503_SERVICE_UNAVAILABLE",
            message="Đã có lỗi xảy ra với hệ thống cơ sở dữ liệu. Vui lòng thử lại sau.",
            details=[
                ErrorDetail(
                    loc=["request", str(request.url)],
                    msg=str(exc),
                    type="sqlalchemy_exception"
                )
            ]
        )
    )
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=error_response.model_dump(exclude_none=True)
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    error_response = ModelResponse(
        success=False,
        error=ErrorResponse(
            code="INTERNAL_SERVER_ERROR",
            message="Đã xảy ra lỗi hệ thống",
            details=[
                ErrorDetail(
                    loc=["internal"],
                    msg=str(exc),
                    type="unhandled_exception",
                )
            ]
        )
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(exclude_none=True)
    )