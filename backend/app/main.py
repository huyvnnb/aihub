import logging
import time

import sentry_sdk
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api.main import api_router
from app.core.config import settings
from app.core.exceptions import NotFoundError, DuplicateEntryError, ApplicationError
from app.utils.handlers import http_exception_handler, general_exception_handler, integrity_error_handler, \
    sqlalchemy_error_handler, not_found_error_handler, duplicate_entry_error_handler, application_error_handler, \
    validation_exception_handler
from app.utils.logger import get_logger, Module

logger = get_logger(Module.APP)


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


@app.on_event("startup")
async def startup_event():
    logger.info("Docs: http://127.0.0.1:8000/docs")

app.add_exception_handler(NotFoundError, not_found_error_handler)
app.add_exception_handler(DuplicateEntryError, duplicate_entry_error_handler)
app.add_exception_handler(ApplicationError, application_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Set all CORS enabled origins
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.middleware("http")
async def log_process_time(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    log_message = f"{request.method} {request.url.path} took {round(duration * 1000, 2)}ms"
    logger.info(log_message)

    return response

app.include_router(api_router, prefix=settings.API_V1_STR)
app.mount("/static", StaticFiles(directory="static"), name="static")

