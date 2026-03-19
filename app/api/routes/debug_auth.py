from fastapi import APIRouter, Depends
from app.api.routes.deps import get_current_student, get_current_user, require_roles

router = APIRouter(prefix="/debug-auth")


@router.get("/student-me")
def student_me(current_student=Depends(get_current_student)):
    return {
        "id": str(current_student.id),
        "matricula": current_student.matricula,
        "email": current_student.email,
    }


@router.get("/user-me")
def user_me(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role.value,
    }


@router.get("/admin-or-intern")
def admin_or_intern(current_user=Depends(require_roles(["admin", "intern"]))):
    return {
        "message": "authorized",
        "email": current_user.email,
        "role": current_user.role.value,
    }