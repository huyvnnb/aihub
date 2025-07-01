import asyncio
from datetime import datetime, timezone, timedelta
from typing import List
from uuid import UUID

from fastapi import BackgroundTasks
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundError, DuplicateEntryError
from app.core.security import get_token_hash, get_password_hash
from app.db.models import User
from app.db.repositories.role_repository import RoleRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.admin_schema import AdminUserCreate
from app.schemas.response_schema import PaginationMeta, Pagination, PaginationParams
from app.schemas.user_schema import UserResponse
from app.services.unit_of_work import UnitOfWork
from app.utils import messages
from app.utils.email_service import send_email
from app.utils.enums import EmailType
from app.utils.token_utils import generate_token


class AdminService:

    async def get_user(self, uow: UnitOfWork, id: UUID) -> UserResponse:
        async with uow:
            existing_user = await uow.users.get_by_id(id)
            if not existing_user:
                raise NotFoundError(messages.User.USER_NOT_FOUND)
            role = await uow.roles.get_by_id(existing_user.role_id)
            if not role:
                raise NotFoundError(messages.Role.ROLE_NOT_FOUND)

        user_data = {
            "id": existing_user.id,
            "email": existing_user.email,
            "fullname": existing_user.fullname,
            "dob": existing_user.dob,
            "address": existing_user.address,
            "avatar": existing_user.avatar,
            "gender": existing_user.gender,
            "verified": existing_user.verified,
            "role": role.name,
            "created_at": existing_user.created_at,
            "updated_at": existing_user.updated_at,
        }

        response = UserResponse.model_validate(user_data)
        return response

    async def get_all_users(self, uow: UnitOfWork, params: PaginationParams) -> Pagination[List[UserResponse]]:
        offset = params.offset
        size = params.size
        page = params.page
        async with uow:
            users, total_items = await uow.users.get_all_users(offset, size)

        user_responses = [
            UserResponse(
                **user.model_dump(),
                role=role
            )
            for user, role in users
        ]

        response = Pagination(
            data=user_responses,
            meta=PaginationMeta(
                page=page,
                size=size,
                total_items=total_items
            )
        )

        return response

    async def create_user(self, uow: UnitOfWork, user_in: AdminUserCreate, background_tasks: BackgroundTasks):
        async with uow:
            # existing_user = await self.user_repo.get_user_by_email(user_in.email)
            # if existing_user:
            #     raise DuplicateEntryError(messages.User.EMAIL_ALREADY_EXISTS)
            existing_role = await uow.roles.get_role_by_name(user_in.role)
            if not existing_role:
                raise NotFoundError(messages.Role.ROLE_NOT_FOUND)

            user_data = user_in.model_dump(exclude={"password", "role"})
            password_hash = await get_password_hash(user_in.password)
            token = await generate_token()
            hashed_token = await get_token_hash(token)
            user = User(
                **user_data,
                password_hash=password_hash,
                role_id=existing_role.id,
                verify_token=hashed_token,
                verify_token_expire=datetime.now(timezone.utc) + timedelta(seconds=settings.VERIFY_TOKEN_EXPIRES)
            )
            await uow.users.create(user)

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

    async def create_many_user(self, uow: UnitOfWork, user_list: List[AdminUserCreate], background_tasks: BackgroundTasks):
        if not user_list:
            return

        async with uow:
            unique_role_names = {user.role for user in user_list}
            role_list = await uow.roles.get_roles_by_names(list(unique_role_names))
            role_map = {role.name: role.id for role in role_list}

            for role_name in unique_role_names:
                if role_name not in role_map:
                    raise NotFoundError(messages.Role.ROLE_NOT_FOUND)

            mapping_tasks = []
            for user_in in user_list:
                role_id = role_map[user_in.role]
                task = self._map_user(user_in, role_id)
                mapping_tasks.append(task)

            mapped_results = await asyncio.gather(*mapping_tasks)
            users = [result[0] for result in mapped_results]
            users_dict = [user.dict(exclude_unset=True) for user in users]
            await uow.users.create_many(users_dict)

        for user_model, raw_token in mapped_results:
            subject = "Verify Your Account"
            email_context = {
                "subject": subject,
                "user_email_placeholder": user_model.email,
                "token": raw_token,
            }
            background_tasks.add_task(
                send_email,
                user_model.email,
                subject,
                EmailType.VERIFY_ACCOUNT.value,
                email_context,
            )

    async def _map_user(self, user_in: AdminUserCreate, role_id: int):
        user_data = user_in.model_dump(exclude={"password", "role"})
        password_hash = await get_password_hash(user_in.password)
        token = await generate_token()
        hashed_token = await get_token_hash(token)
        user = User(
            **user_data,
            password_hash=password_hash,
            role_id=role_id,
            verify_token=hashed_token,
            verify_token_expire=datetime.now(timezone.utc) + timedelta(seconds=settings.VERIFY_TOKEN_EXPIRES)
        )
        return user, token


def get_admin_service():
    return AdminService()

