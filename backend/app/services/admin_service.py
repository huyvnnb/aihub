from uuid import UUID

from fastapi import Depends, HTTPException
from starlette import status

from app.db.repositories.role_repository import RoleRepository, get_role_repo
from app.db.repositories.user_repository import UserRepository, get_user_repo
from app.schemas.user_schema import UserResponse


class AdminService:
    def __init__(self,
                 user_repo: UserRepository = Depends(get_user_repo),
                 role_repo: RoleRepository = Depends(get_role_repo)
                 ):
        self.user_repo = user_repo
        self.role_repo = role_repo

    def get_user(self, id: UUID):
        try:
            existing_user = self.user_repo.get_user(id)
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not exist"
                )
            role = self.role_repo.get_role(existing_user.role_id)
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Role not exist"
                )

            user_data = {
                "id": existing_user.id,
                "email": existing_user.email,
                "fullname": existing_user.fullname,
                "dob": existing_user.dob,
                "address": existing_user.address,
                "avatar": existing_user.avatar,
                "gender": existing_user.gender,
                "verified": existing_user.verified,
                "role": role.name,
                "created_at": existing_user.created_at,
                "updated_at": existing_user.updated_at,
            }

            response = UserResponse.model_validate(user_data)
            return response

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )