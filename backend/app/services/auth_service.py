from datetime import datetime

from fastapi import Depends, HTTPException, status, BackgroundTasks

from app.core.config import settings
from app.core.security import get_password_hash, get_token_hash
from app.db.models import User
from app.db.repositories.role_repository import RoleRepository, get_role_repo
from app.db.repositories.user_repository import UserRepository, get_user_repo
from app.schemas.user_schema import UserCreate
from app.utils.constants import DEFAULT_ROLE
from app.utils.email_service import send_email
from app.utils.enums import EmailType
from app.utils.token_utils import generate_token


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository = Depends(get_user_repo),
        role_repo: RoleRepository = Depends(get_role_repo)
    ):
        self.user_repo = user_repo
        self.role_repo = role_repo

    def register(self, user_in: UserCreate, background_tasks: BackgroundTasks):
        existing_user = self.user_repo.get_user_by_email(user_in.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already existed"
            )
        user_data = user_in.model_dump(exclude={"password"})
        password_hash = get_password_hash(user_in.password)
        existing_role = self.role_repo.get_role_by_name(DEFAULT_ROLE)
        if not existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role {DEFAULT_ROLE} not exist"
            )
        token = generate_token()
        hashed_token = get_token_hash(token)
        user = User(
            **user_data,
            password_hash=password_hash,
            role_id=existing_role.id,
            verify_token=hashed_token
        )

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
            "current_year": str(datetime.now().year)
        }
        background_tasks.add_task(
            send_email, user.email, subject, EmailType.VERIFY_ACCOUNT.value, email_context
        )
        return self.user_repo.create(user)


