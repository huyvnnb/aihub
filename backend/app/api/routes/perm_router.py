from types import NoneType

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.api.deps import AsyncSessionDep, get_uow, require_permission
from app.core.db import get_session
from app.schemas.perm_schema import PermResponse, PermCreate
from app.schemas.response_schema import ModelResponse
from app.services.permission_service import PermissionService, get_perm_service
from app.utils import messages
from app.utils.constants import P

router = APIRouter(
    prefix="/permission",
    tags=["Permission"]
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ModelResponse[NoneType],
    response_model_exclude_none=True
)
async def create_perm(perm_in: PermCreate, perm_service=Depends(get_perm_service), uow=Depends(get_uow)):
    await perm_service.create_perm(uow, perm_in)

    return ModelResponse(
        message=messages.Permission.CREATED_SUCCESS.format(permission_name=perm_in.name)
    )


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=ModelResponse[PermResponse],
    response_model_exclude_none=True,
    dependencies=[Depends(require_permission(P.USER_READ))]
)
async def get_perm_by_id(id: int, perm_service=Depends(get_perm_service), uow=Depends(get_uow)):
    response = await perm_service.get_perm_by_id(uow, id)

    return ModelResponse(
        message=messages.Permission.FETCHED_SUCCESS,
        data=response
    )
