from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from app.schemas.response_schema import ModelResponse, PaginationParams
from app.schemas.user_schema import UserResponse
from app.services.admin_service import AdminService

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)


@router.get("/users/{id}",
            status_code=status.HTTP_200_OK,
            response_model=ModelResponse[UserResponse],
            response_model_exclude_none=True
            )
async def get_user(id: UUID, admin_service: AdminService = Depends(AdminService)):
    user = admin_service.get_user(id=id)
    return ModelResponse(
        message="Fetch user successfully",
        data=user
    )


@router.get("/users",
            status_code=status.HTTP_200_OK,
            response_model=ModelResponse[List[UserResponse]],
            response_model_exclude_none=True
            )
async def get_all_users(pagination: PaginationParams = Depends(), admin_service: AdminService = Depends()):
    page = pagination.page
    size = pagination.size
    response = admin_service.get_all_users(page, size)

    return ModelResponse(
        message="Fetch users list successfully",
        data=response.data,
        meta=response.meta
    )
