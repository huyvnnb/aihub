from fastapi import APIRouter, Depends
from starlette import status

from app.schemas.role_schema import RoleCreate
from app.services.role_service import RoleService

router = APIRouter(
    prefix="/role",
    tags=["Role"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_role(
        role_data: RoleCreate,
        role_service: RoleService = Depends(RoleService)
):
    role_service.create_role(role_data)
