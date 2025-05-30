from types import NoneType

from fastapi import APIRouter, status, Depends, BackgroundTasks

from app.schemas.response_schema import ModelResponse
from app.schemas.user_schema import UserCreate
from app.services.auth_service import AuthService
from app.utils import messages

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=ModelResponse[NoneType],
    response_model_exclude_none=True
)
async def register(user_data: UserCreate, background_tasks: BackgroundTasks, auth_service: AuthService = Depends()):
    auth_service.register(user_data, background_tasks)
    return ModelResponse(
        message=messages.Auth.REGISTRATION_SUCCESS
    )
