from uuid import UUID

from fastapi import APIRouter, Depends
from starlette import status

from app.schemas.response_schema import ModelResponse
from app.schemas.user_schema import UserResponse
from app.services.admin_service import AdminService

router = APIRouter(
    prefix="/admin",
    tags=["Admin"]
)

@router.get("/users/{id}",
    status_code=status.HTTP_200_OK,
    response_model=ModelResponse[UserResponse]
)
async def get_user(id: UUID, user_service: AdminService = Depends(AdminService)):
    user = user_service.get_user(id=id)
    return ModelResponse[UserResponse](
        message="Fetch user successfully",
        data=user
    )


