from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.api.deps import AsyncSessionDep, get_uow
from app.core.db import get_session
from app.schemas.response_schema import ModelResponse
from app.schemas.role_schema import RoleCreate, RoleResponse
from app.services.role_service import RoleService, get_role_service
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
async def create_role(role_in: RoleCreate, uow=Depends(get_uow), role_service=Depends(get_role_service)):
    response = await role_service.create_role(uow, role_in)
    return ModelResponse(
        message=messages.Role.CREATED_SUCCESS.format(role_name=response.name),
        data=response
    )
