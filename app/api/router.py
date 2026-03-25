from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.auth_students import router as auth_students_router
from app.api.routes.auth_users import router as auth_users_router
from app.api.routes.debug_auth import router as debug_auth_router
from app.api.routes.opportunities import router as opportunities_router
from app.api.routes.periods import router as periods_router
from app.api.routes.students import router as students_router
from app.api.routes.admin_opportunities import router as admin_opportunities_router
from app.api.routes.partner import router as partner_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_students_router, tags=["students-auth"])
api_router.include_router(auth_users_router, tags=["users-auth"])
api_router.include_router(debug_auth_router, tags=["debug-auth"])
api_router.include_router(opportunities_router, tags=["opportunities"])
api_router.include_router(periods_router, tags=["periods"])
api_router.include_router(students_router, tags=["students"])
api_router.include_router(admin_opportunities_router, tags=["admin-opportunities"])
api_router.include_router(partner_router, tags=["partner"])
