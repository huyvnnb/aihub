import asyncio
import uuid
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status, BackgroundTasks, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core import security
from app.core.config import settings
from app.core.exceptions import NotFoundError, DuplicateEntryError
from app.core.security import get_password_hash, get_token_hash, verify_password, verify_token
from app.db.models import User, RFToken
from app.schemas.auth_schema import RegisterRequest, LoginRequest, VerifyRequest, LoginResponse, EmailRequest
from app.schemas.token_schema import VerifyToken
from app.services.unit_of_work import UnitOfWork
from app.utils import messages
from app.utils.constants import DEFAULT_ROLE
from app.utils.email_service import send_email
from app.utils.enums import EmailType, Module
from app.utils.logger import get_logger
from app.utils.token_utils import generate_token, generate_jwt_token, get_client_meta

logger = get_logger(Module.AUTH_SERVICE)


class AuthService:
    async def register(self, uow: UnitOfWork, user_in: RegisterRequest, background_tasks: BackgroundTasks) -> None:
        logger.info("Check user exist")
        async with uow:
            existing_user = await uow.users.get_user_by_email(user_in.email)
            if existing_user:
                raise DuplicateEntryError(messages.User.EMAIL_ALREADY_EXISTS)
            password_hash = await get_password_hash(user_in.password)

            logger.info("In transaction create user")
            user_data = user_in.model_dump(exclude={"password"})
            existing_role = await uow.roles.get_role_by_name(DEFAULT_ROLE)
            # if not existing_role:
            #     # raise SystemConfigurationError(...)
            token = security.generate_token()
            hashed_token = security.get_token_hash(token)
            user = User(
                **user_data,
                password_hash=password_hash,
                role_id=existing_role.id,
                verify_token=hashed_token,
                verify_token_expire=datetime.now(timezone.utc) + timedelta(seconds=settings.VERIFY_TOKEN_EXPIRES)
            )
            await uow.users.create(user)
        logger.info("End transaction")
        logger.info("Send email to user")
        # Context data
        subject = "Verify Your Account"
        verification_url = f"{settings.PROJECT_URL}/email/verify?token={token}"
        email_context = {
            "subject": subject,
            "user_email_placeholder": user_in.email,
            "verification_url": verification_url,
        }
        background_tasks.add_task(
            send_email, user.email, subject, EmailType.VERIFY_ACCOUNT.value, email_context
        )

    async def login(self, uow: UnitOfWork, login: LoginRequest, request: Request) -> LoginResponse:
        async with uow:
            existing_user = await uow.users.get_user_by_email(login.email)

        if not existing_user:
            raise NotFoundError(messages.User.USER_NOT_FOUND)
        match = await verify_password(login.password, existing_user.password_hash)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=messages.Auth.LOGIN_FAILED
            )

        if not existing_user.verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=messages.Auth.ACCOUNT_NOT_YET_ACTIVE
            )

        refresh_token_task = generate_jwt_token(existing_user.id, settings.REFRESH_TOKEN_EXPIRES)
        access_token_task = generate_jwt_token(existing_user.id, settings.ACCESS_TOKEN_EXPIRES)
        refresh_token, access_token = await asyncio.gather(
            refresh_token_task,
            access_token_task
        )
        async with uow:
            save_token = self._build_refresh_token(existing_user.id, refresh_token, request)
            await uow.rftoken.create(save_token)
        return LoginResponse(
            refresh_token=refresh_token,
            access_token=access_token
        )

    def _build_refresh_token(self, user_id: uuid.UUID, refresh_token: str, request: Request) -> RFToken:
        token_hash = get_token_hash(refresh_token)
        ip, user_agent = get_client_meta(request)
        return RFToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRES),
            ip_address=ip,
            user_agent=user_agent,
        )

    async def oauth2_login(self, uow: UnitOfWork, login: LoginRequest, request: Request):
        async with uow:
            logger.info("IN UOW 1")
            existing_user = await uow.users.get_user_by_email(login.email)
        if not existing_user:
            raise NotFoundError(messages.User.USER_NOT_FOUND)
        match = await verify_password(login.password, existing_user.password_hash)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=messages.Auth.LOGIN_FAILED
            )

        if not existing_user.verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=messages.Auth.ACCOUNT_NOT_YET_ACTIVE
            )

        refresh_token_task = generate_jwt_token(existing_user.id, settings.REFRESH_TOKEN_EXPIRES)
        access_token_task = generate_jwt_token(existing_user.id, settings.ACCESS_TOKEN_EXPIRES)
        refresh_token, access_token = await asyncio.gather(
            refresh_token_task,
            access_token_task
        )
        async with uow:
            logger.info("IN UOW 2")
            save_token = self._build_refresh_token(existing_user.id, refresh_token, request)
            await uow.rftoken.create(save_token)
        return access_token

    async def verify_account(self, uow: UnitOfWork, token: VerifyToken):
        hash_token = security.get_token_hash(token.token)
        async with uow:
            existing_user = await uow.users.get_user_by_token(hash_token)
            if not existing_user:
                raise NotFoundError(messages.Auth.INVALID_TOKEN)

            verified = security.verify_token(existing_user.verify_token, token.token, existing_user.verify_token_expire)
            if verified:
                existing_user.verified = True
                existing_user.verify_token = None
                existing_user.verify_token_expire = None
                await uow.users.update(existing_user)

    async def resend_email(self, uow: UnitOfWork, email_request: EmailRequest, subject: str,
                           background_tasks: BackgroundTasks):
        async with uow:
            existing_user = await uow.users.get_user_by_email(email_request.email)
            if not existing_user:
                raise NotFoundError(messages.User.USER_NOT_FOUND)

            if existing_user.verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=messages.Auth.EMAIL_ALREADY_VERIFIED
                )

            token = security.generate_token()
            token_hash = security.get_token_hash(token)
            existing_user.verify_token = token_hash
            existing_user.verify_token_expire = (
                    datetime.now(timezone.utc) + timedelta(seconds=settings.VERIFY_TOKEN_EXPIRES)
            )
            await uow.users.update(existing_user)

        subject = "Verify Your Account"
        verification_url = f"{settings.PROJECT_URL}/email/verify?token={token}"
        email_context = {
            "subject": subject,
            "user_email_placeholder": email_request.email,
            "verification_url": verification_url,
        }
        background_tasks.add_task(
            send_email, email_request.email, subject, EmailType.VERIFY_ACCOUNT.value, email_context
        )

    # async def forgot_password(self, request: EmailRequest):
    #     existing_user = self.user_repo.get_user_by_email(request.email)
    #     if not existing_user:
    #         raise NotFoundError(messages.User.USER_NOT_FOUND)

    # Optimize login

    # async def process_refresh_token() -> tuple[str, RFToken]:
    #     # a. Tạo RFT
    #     rft = await generate_jwt_token(existing_user.id, settings.REFRESH_TOKEN_EXPIRES)
    #     # b. Hash RFT
    #     rft_hash = await get_token_hash(rft)
    #     # c. Chuẩn bị đối tượng để lưu
    #     ip, user_agent = get_client_meta(request)
    #     save_token_obj = RFToken(
    #         user_id=existing_user.id,
    #         token_hash=rft_hash,
    #         expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRES),
    #         ip_address=ip,
    #         user_agent=user_agent,
    #     )
    #     return rft, save_token_obj
    #
    # refresh_token_logic_task = process_refresh_token()
    #
    # # Chạy cả hai task chính đồng thời
    # results = await asyncio.gather(
    #     access_token_task,
    #     refresh_token_logic_task
    # )


def get_auth_service():
    return AuthService()
