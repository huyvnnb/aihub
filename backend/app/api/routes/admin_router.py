from types import NoneType
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, BackgroundTasks
from starlette import status

from app.api.deps import AsyncSessionDep, CurrentUser, require_permission
from app.schemas.admin_schema import AdminUserCreate
from app.schemas.response_schema import ModelResponse, PaginationParams
from app.schemas.user_schema import UserResponse
from app.services.admin_service import AdminService
from app.utils import messages
from app.utils.constants import P

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/users/{id}",
            status_code=status.HTTP_200_OK,
            response_model=ModelResponse[UserResponse],
            response_model_exclude_none=True,
            dependencies=[Depends(require_permission(P.USER_READ))]
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
            response_model_exclude_none=True,
            dependencies=[Depends(require_permission(P.USER_READ_LIST))]
            )
async def get_all_users(session: AsyncSessionDep, params: PaginationParams = Depends()):
    admin_service = AdminService(session)
    response = await admin_service.get_all_users(params)

    return ModelResponse(
        message=messages.Admin.FETCH_USER_LIST,
        data=response.data,
        meta=response.meta
    )


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=ModelResponse[NoneType],
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission(P.USER_CREATE))]
)
async def create_user(session: AsyncSessionDep, user_in: AdminUserCreate, background_tasks: BackgroundTasks):
    admin_service = AdminService(session)
    await admin_service.create_user(user_in, background_tasks)

    return ModelResponse(
        message=messages.Admin.CREATE_USER.format(role_name=user_in.role)
    )


@router.post(
    "/users/bulk",
    status_code=status.HTTP_201_CREATED,
    response_model=ModelResponse[NoneType],
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission(P.USER_CREATE_LIST))]
)
async def create_many_users(session: AsyncSessionDep, user_list: List[AdminUserCreate], background_tasks: BackgroundTasks):
    admin_service = AdminService(session)
    await admin_service.create_many_user(user_list, background_tasks)

    return ModelResponse(
        message=messages.User.CREATED_MANY_SUCCESS
    )