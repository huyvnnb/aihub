from types import NoneType
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, BackgroundTasks
from starlette import status

from app.api.deps import require_permission, get_uow
from app.schemas.admin_schema import AdminUserCreate
from app.schemas.response_schema import ModelResponse, PaginationParams
from app.schemas.user_schema import UserResponse
from app.services.admin_service import get_admin_service
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
async def get_user(id: UUID, uow=Depends(get_uow), admin_service=Depends(get_admin_service)):
    user = await admin_service.get_user(uow=uow, id=id)
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
async def get_all_users(params: PaginationParams = Depends(), uow=Depends(get_uow), admin_service=Depends(get_admin_service)):
    response = await admin_service.get_all_users(uow, params)

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
    # dependencies=[Depends(require_permission(P.USER_CREATE))]
)
async def create_user(user_in: AdminUserCreate, background_tasks: BackgroundTasks, uow=Depends(get_uow), admin_service=Depends(get_admin_service)):
    await admin_service.create_user(uow, user_in, background_tasks)

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
async def create_many_users(user_list: List[AdminUserCreate], background_tasks: BackgroundTasks, uow=Depends(get_uow), admin_service=Depends(get_admin_service)):
    await admin_service.create_many_user(uow, user_list, background_tasks)

    return ModelResponse(
        message=messages.User.CREATED_MANY_SUCCESS
    )
