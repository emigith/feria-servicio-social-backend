from pydantic import BaseModel, EmailStr, Field


class StudentRegisterRequest(BaseModel):
    matricula: str = Field(min_length=1)
    correo: EmailStr
    password: str = Field(min_length=8)
    nombre: str = Field(min_length=1)
    apellido: str = Field(min_length=1)


class StudentLoginRequest(BaseModel):
    matricula: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UserLoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str