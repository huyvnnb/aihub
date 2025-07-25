from fastapi import APIRouter

from app.api.routes import (items, login, private, users, utils,
                            auth_router, role_router, admin_router, perm_router, youtube_router, image_router,
                            chat_router)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(auth_router.router)
api_router.include_router(role_router.router)
api_router.include_router(admin_router.router)
api_router.include_router(perm_router.router)
api_router.include_router(youtube_router.router)
api_router.include_router(image_router.router)
api_router.include_router(chat_router.router)
# if settings.ENVIRONMENT == "local":
#     api_router.include_router(private.router)
