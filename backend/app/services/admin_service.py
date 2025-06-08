from typing import List
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.core.exceptions import NotFoundError
from app.db.repositories.role_repository import RoleRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.response_schema import PaginationMeta, Pagination, PaginationParams
from app.schemas.user_schema import UserResponse
from app.utils import messages


class AdminService:
    def __init__(self, session: AsyncSession):
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)

    async def get_user(self, id: UUID) -> UserResponse:
        existing_user = await self.user_repo.get_by_id(id)
        if not existing_user:
            raise NotFoundError(
                entity_name="USER",
                entity_id=id
            )
        role = await self.role_repo.get_by_id(existing_user.role_id)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=messages.Role.ROLE_NOT_FOUND
            )

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

    async def get_all_users(self, params: PaginationParams) -> Pagination[List[UserResponse]]:
        offset = params.offset
        size = params.size
        page = params.page
        users, total_items = await self.user_repo.get_all_users(offset, size)

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
