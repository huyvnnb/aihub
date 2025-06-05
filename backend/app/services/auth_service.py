from datetime import datetime, timezone, timedelta

from fastapi import Depends, HTTPException, status, BackgroundTasks, Request
from pydantic import EmailStr

from app.core.config import settings
from app.core.security import get_password_hash, get_token_hash, verify_password, verify_token
from app.db.models import User, RFToken
from app.db.repositories.rftoken_repository import RFTokenRepository, get_rftoken_repo
from app.db.repositories.role_repository import RoleRepository, get_role_repo
from app.db.repositories.user_repository import UserRepository, get_user_repo
from app.schemas.auth_schema import RegisterRequest, LoginRequest, VerifyRequest, LoginResponse, EmailRequest
from app.utils import messages
from app.utils.constants import DEFAULT_ROLE
from app.utils.email_service import send_email
from app.utils.enums import EmailType
from app.utils.token_utils import generate_token, generate_jwt_token, get_client_meta


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository = Depends(get_user_repo),
        role_repo: RoleRepository = Depends(get_role_repo),
        rftoken_repo: RFTokenRepository = Depends(get_rftoken_repo)
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.rftoken_repo = rftoken_repo

    def register(self, user_in: RegisterRequest, background_tasks: BackgroundTasks) -> None:
        existing_user = self.user_repo.get_user_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages.User.EMAIL_ALREADY_EXISTS
            )
        user_data = user_in.model_dump(exclude={"password"})
        password_hash = get_password_hash(user_in.password)
        existing_role = self.role_repo.get_role_by_name(DEFAULT_ROLE)
        if not existing_role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.Role.ROLE_NOT_FOUND
            )
        token = generate_token()
        hashed_token = get_token_hash(token)
        user = User(
            **user_data,
            password_hash=password_hash,
            role_id=existing_role.id,
            verify_token=hashed_token,
            verify_token_expire=datetime.now(timezone.utc) + timedelta(seconds=settings.VERIFY_TOKEN_EXPIRES)
        )
        self.user_repo.create(user)

        # Context data
        subject = "Verify Your Account"
        app_name = settings.PROJECT_NAME
        website_url = settings.PROJECT_URL
        email_context = {
            "subject": subject,
            "app_name": app_name,
            "user_email_placeholder": user_in.email,
            "token": token,
            "website_url": website_url,
        }
        background_tasks.add_task(
            send_email, user.email, subject, EmailType.VERIFY_ACCOUNT.value, email_context
        )

    def login(self, login: LoginRequest, request: Request) -> LoginResponse:
        existing_user = self.user_repo.get_user_by_email(login.email)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.User.EMAIL_NOT_EXISTS
            )
        match = verify_password(login.password, existing_user.password_hash)
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

        refresh_token = generate_jwt_token(existing_user.id, settings.REFRESH_TOKEN_EXPIRES)
        access_token = generate_jwt_token(existing_user.id, settings.ACCESS_TOKEN_EXPIRES)
        token_hash = get_token_hash(refresh_token)
        ip, user_agent = get_client_meta(request)
        save_token = RFToken(
            user_id= existing_user.id,
            token_hash=token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRES),
            ip_address=ip,
            user_agent=user_agent,
        )
        self.rftoken_repo.create(save_token)
        return LoginResponse(
            refresh_token=refresh_token,
            access_token=access_token
        )

    def verify_account(self, verify: VerifyRequest):
        existing_user = self.user_repo.get_user_by_email(verify.email)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.User.EMAIL_NOT_EXISTS
            )
        match = verify_token(verify.token, existing_user.verify_token)
        if not match:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=messages.Auth.INVALID_TOKEN
            )
        existing_user.verified = True
        existing_user.verify_token = None
        existing_user.verify_token_expire = None
        self.user_repo.update(existing_user)

    def resend_email(self, email_request: EmailRequest, subject: str, background_tasks: BackgroundTasks):
        email = email_request.email
        existing_user = self.user_repo.get_user_by_email(email)
        if not existing_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.User.EMAIL_NOT_EXISTS
            )
        if existing_user.verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=messages.Auth.EMAIL_ALREADY_VERIFIED
            )

        token = generate_token()
        token_hash = get_token_hash(token)
        existing_user.verify_token = token_hash
        existing_user.verify_token_expire = datetime.now(timezone.utc) + timedelta(seconds=settings.VERIFY_TOKEN_EXPIRES)
        self.user_repo.update(existing_user)

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



