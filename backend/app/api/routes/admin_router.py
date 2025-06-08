from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.api.deps import AsyncSessionDep
from app.core.db import get_session
from app.schemas.response_schema import ModelResponse, PaginationParams
from app.schemas.user_schema import UserResponse
from app.services.admin_service import AdminService
from app.utils import messages

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/users/{id}",
            status_code=status.HTTP_200_OK,
            response_model=ModelResponse[UserResponse],
            response_model_exclude_none=True
            )
async def get_user(id: UUID, session: AsyncSessionDep):
    admin_service = AdminService(session)
    user = await admin_service.get_user(id=id)
    return ModelResponse(
        message=messages.Admin.FETCH_USER,
        data=user
    )


@router.get("/users",
            status_code=status.HTTP_200_OK,
            response_model=ModelResponse[List[UserResponse]],
            response_model_exclude_none=True
            )
async def get_all_users(session: AsyncSessionDep, params: PaginationParams = Depends()):
    admin_service = AdminService(session)
    response = await admin_service.get_all_users(params)

    return ModelResponse(
        message=messages.Admin.FETCH_USER_LIST,
        data=response.data,
        meta=response.meta
    )
