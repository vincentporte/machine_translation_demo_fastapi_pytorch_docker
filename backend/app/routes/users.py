from fastapi import APIRouter, Depends, HTTPException

from app.database.models import UserDB
from app.services.users import current_active_user, fastapi_users, jwt_authentication

router = APIRouter()

router.include_router(fastapi_users.get_auth_router(jwt_authentication), prefix="/auth")
router.include_router(fastapi_users.get_register_router(), prefix="/auth")
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
)
router.include_router(
    fastapi_users.get_verify_router(),
    prefix="/auth",
)
router.include_router(fastapi_users.get_users_router(), prefix="/users")
