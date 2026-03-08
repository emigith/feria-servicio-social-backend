from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.auth_students import router as auth_students_router
from app.api.routes.auth_users import router as auth_users_router
from app.api.routes.debug_auth import router as debug_auth_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_students_router, tags=["students-auth"])
api_router.include_router(auth_users_router, tags=["users-auth"])
api_router.include_router(debug_auth_router, tags=["debug-auth"])