import asyncio
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status, BackgroundTasks, Request
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError, DuplicateEntryError
from app.core.security import get_password_hash, get_token_hash, verify_password, verify_token
from app.db.models import User, RFToken
from app.db.repositories.rftoken_repository import RFTokenRepository
from app.db.repositories.role_repository import RoleRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.auth_schema import RegisterRequest, LoginRequest, VerifyRequest, LoginResponse, EmailRequest
from app.utils import messages
from app.utils.constants import DEFAULT_ROLE
from app.utils.email_service import send_email
from app.utils.enums import EmailType
from app.utils.token_utils import generate_token, generate_jwt_token, get_client_meta


class AuthService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)
        self.rftoken_repo = RFTokenRepository(session)

    async def register(self, user_in: RegisterRequest, background_tasks: BackgroundTasks) -> None:
        existing_user = await self.user_repo.get_user_by_email(user_in.email)
        if existing_user:
            raise DuplicateEntryError(messages.User.EMAIL_ALREADY_EXISTS)

        user_data = user_in.model_dump(exclude={"password"})
        password_hash = await get_password_hash(user_in.password)
        existing_role = await self.role_repo.get_role_by_name(DEFAULT_ROLE)
        # if not existing_role:
        #     # raise SystemConfigurationError(...)
        token = await generate_token()
        hashed_token = await get_token_hash(token)
        user = User(
            **user_data,
            password_hash=password_hash,
            role_id=existing_role.id,
            verify_token=hashed_token,
            verify_token_expire=datetime.now(timezone.utc) + timedelta(seconds=settings.VERIFY_TOKEN_EXPIRES)
        )
        await self.user_repo.create(user)

        # Context data
        subject = "Verify Your Account"
        email_context = {
            "subject": subject,
            "user_email_placeholder": user_in.email,
            "token": token,
        }
        background_tasks.add_task(
            send_email, user.email, subject, EmailType.VERIFY_ACCOUNT.value, email_context
        )

    async def login(self, login: LoginRequest, request: Request) -> LoginResponse:
        existing_user = await self.user_repo.get_user_by_email(login.email)
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
        token_hash = await get_token_hash(refresh_token)
        ip, user_agent = get_client_meta(request)
        save_token = RFToken(
            user_id=existing_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRES),
            ip_address=ip,
            user_agent=user_agent,
        )
        await self.rftoken_repo.create(save_token)
        return LoginResponse(
            refresh_token=refresh_token,
            access_token=access_token
        )

    async def oauth2_login(self, login: LoginRequest, request: Request):
        existing_user = await self.user_repo.get_user_by_email(login.email)
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
        token_hash = await get_token_hash(refresh_token)
        ip, user_agent = get_client_meta(request)
        save_token = RFToken(
            user_id=existing_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRES),
            ip_address=ip,
            user_agent=user_agent,
        )
        await self.rftoken_repo.create(save_token)
        return access_token

    async def verify_account(self, verify: VerifyRequest):
        existing_user = await self.user_repo.get_user_by_email(verify.email)
        if not existing_user:
            raise NotFoundError(messages.User.USER_NOT_FOUND)

        match = await verify_token(verify.token, existing_user.verify_token)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=messages.Auth.INVALID_TOKEN
            )
        existing_user.verified = True
        existing_user.verify_token = None
        existing_user.verify_token_expire = None
        await self.user_repo.update(existing_user)

    async def resend_email(self, email_request: EmailRequest, subject: str, background_tasks: BackgroundTasks):
        email = email_request.email
        existing_user = await self.user_repo.get_user_by_email(email)
        if not existing_user:
            raise NotFoundError(messages.User.USER_NOT_FOUND)

        if existing_user.verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages.Auth.EMAIL_ALREADY_VERIFIED
            )

        token = await generate_token()
        token_hash = await get_token_hash(token)
        existing_user.verify_token = token_hash
        existing_user.verify_token_expire = (
                datetime.now(timezone.utc) + timedelta(seconds=settings.VERIFY_TOKEN_EXPIRES)
        )
        await self.user_repo.update(existing_user)

        app_name = settings.PROJECT_NAME
        website_url = settings.PROJECT_URL
        email_context = {
            "subject": subject,
            "app_name": app_name,
            "user_email_placeholder": email,
            "token": token,
            "website_url": website_url,
        }
        background_tasks.add_task(
            send_email, email, subject, EmailType.VERIFY_ACCOUNT.value, email_context
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