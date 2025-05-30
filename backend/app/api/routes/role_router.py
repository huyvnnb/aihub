from fastapi import APIRouter, Depends
from starlette import status

from app.schemas.response_schema import ModelResponse
from app.schemas.role_schema import RoleCreate, RoleResponse
from app.services.role_service import RoleService
from app.utils import messages

router = APIRouter(
    prefix="/role",
    tags=["Role"]
)


@router.post("/",
             status_code=status.HTTP_201_CREATED,
             response_model=ModelResponse[RoleResponse],
             response_model_exclude_none=True
             )
def create_role(
        role_data: RoleCreate,
        role_service: RoleService = Depends(),
):
    response = role_service.create_role(role_data)
    return ModelResponse(
        message=messages.Role.CREATED_SUCCESS.format(role_name=response.name),
        data=response
    )
