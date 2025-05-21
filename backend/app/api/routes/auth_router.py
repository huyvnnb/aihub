from types import NoneType

from fastapi import APIRouter, status, Depends

from app.schemas.response_schema import ModelResponse
from app.schemas.user_schema import UserCreate
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ModelResponse[NoneType],
    response_model_exclude_none=True
)
async def register(user_data: UserCreate, auth_service: AuthService = Depends(AuthService)):
    auth_service.register(user_data)
    return ModelResponse[NoneType](
        message="Register successfully"
    )
