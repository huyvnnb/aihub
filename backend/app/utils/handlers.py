from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette import status
import logging
logger = logging.getLogger(__name__)


from app.schemas.response_schema import ModelResponse, ErrorResponse, ErrorDetail


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    # if not isinstance(exc, HTTPException):
    #     logger.error(f"Unexpected exception type {type(exc)} in http_exception_handler: {exc}", exc_info=True)
    #     return JSONResponse(
    #         status_code=500,
    #         content=ModelResponse(
    #             success=False,
    #             error=ErrorResponse(code="INTERNAL_SERVER_ERROR", message="An unexpected internal error occurred.")
    #         ).model_dump()
    #     )
    # logger.error(
    #     f"HTTP Exception: {exc.status_code} - {exc.detail} for URL: {request.url}",
    #     exc_info=True
    # )
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