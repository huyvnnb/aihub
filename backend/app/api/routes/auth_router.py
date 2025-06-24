from types import NoneType

from fastapi import APIRouter, status, Depends, BackgroundTasks, Request, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.deps import AsyncSessionDep
from app.core.db import get_session
from app.schemas.auth_schema import RegisterRequest, LoginResponse, LoginRequest, VerifyRequest, ResendRequest, \
    EmailRequest
from app.schemas.response_schema import ModelResponse
from app.schemas.user_schema import UserCreate
from app.services.auth_service import AuthService
from app.utils import messages

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ModelResponse[NoneType],
    response_model_exclude_none=True
)
async def register(user_data: RegisterRequest, background_tasks: BackgroundTasks, session: AsyncSession = Depends(get_session)):
    auth_service = AuthService(session)
    await auth_service.register(user_data, background_tasks)
    return ModelResponse(
        message=messages.Auth.REGISTRATION_SUCCESS
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=ModelResponse[LoginResponse],
    response_model_exclude_none=True
)
async def login(request: Request, login: LoginRequest, session: AsyncSession = Depends(get_session)) :
    auth_service = AuthService(session)
    response = await auth_service.login(login, request)
    return ModelResponse(
        message=messages.Auth.LOGIN_SUCCESS,
        data=response
    )


@router.post("/login/access-token")
async def login_access_token(request: Request, session: AsyncSessionDep, form_data: OAuth2PasswordRequestForm = Depends()):
    auth_service = AuthService(session)
    token = await auth_service.oauth2_login(
        LoginRequest(email=form_data.username, password=form_data.password), request
    )
    if not token:
        raise HTTPException(status_code=400, detail="Something has occurred")

    return {"access_token": token, "token_type": "bearer"}


@router.post(
    "/email/verify",
    status_code=status.HTTP_200_OK,
    response_model=ModelResponse[NoneType],
    response_model_exclude_none=True
)
async def verify_account(verify: VerifyRequest, session: AsyncSessionDep):
    auth_service = AuthService(session)
    await auth_service.verify_account(verify)
    return ModelResponse(
        message=messages.Auth.EMAIL_VERIFICATION_SUCCESS
    )


@router.post(
    "/verify/resend",
    status_code=status.HTTP_200_OK,
    response_model=ModelResponse[NoneType],
    response_model_exclude_none=True
)
async def resend_verify_email(resend: EmailRequest, background_tasks: BackgroundTasks, session: AsyncSessionDep):
    subject = "Verify Your Account"
    auth_service = AuthService(session)
    await auth_service.resend_email(resend, subject, background_tasks)
    return ModelResponse(
        message=messages.Auth.VERIFICATION_EMAIL_SENT
    )



