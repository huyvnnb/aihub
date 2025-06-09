from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.api.deps import AsyncSessionDep
from app.core.db import get_session
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
async def create_role(role_data: RoleCreate, session: AsyncSessionDep):
    role_service = RoleService(session)
    response = await role_service.create_role(role_data)
    return ModelResponse(
        message=messages.Role.CREATED_SUCCESS.format(role_name=response.name),
        data=response
    )
