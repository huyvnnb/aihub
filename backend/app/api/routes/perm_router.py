from types import NoneType

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette import status

from app.api.deps import AsyncSessionDep
from app.core.db import get_session
from app.schemas.perm_schema import PermResponse, PermCreate
from app.schemas.response_schema import ModelResponse
from app.services.permission_service import PermissionService
from app.utils import messages

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
async def create_perm(perm_in: PermCreate, session: AsyncSessionDep):
    perm_service = PermissionService(session)
    await perm_service.create_perm(perm_in)

    return ModelResponse(
        message=messages.Permission.CREATED_SUCCESS.format(permission_name=perm_in.name)
    )


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=ModelResponse[PermResponse],
    response_model_exclude_none=True
)
async def get_perm_by_id(id: int, session: AsyncSession = Depends(get_session)):
    perm_service = PermissionService(session)
    response = await perm_service.get_perm_by_id(id)

    return ModelResponse(
        message=messages.Permission.FETCHED_SUCCESS,
        data=response
    )