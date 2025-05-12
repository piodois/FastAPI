from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re


class UsuarioBase(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    username: str = Field(..., min_length=3, max_length=50,
                          description="Nombre de usuario (3-50 caracteres)")

    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('El nombre de usuario debe contener solo letras, números y guiones bajos')
        return v


class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8, max_length=100,
                          description="Contraseña (mínimo 8 caracteres)")
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    is_active: bool = True
    is_admin: bool = True

    @validator('password')
    def password_strength(cls, v):
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&+_\-.])[A-Za-z\d@$!%*?&+_\-.]{8,}$', v):
            raise ValueError(
                'La contraseña debe tener al menos 8 caracteres, una letra mayúscula, una letra minúscula, un número y un carácter especial')
        return v


class UsuarioUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    apellido: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None

    @validator('password')
    def password_strength(cls, v):
        if v is not None and not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', v):
            raise ValueError(
                'La contraseña debe tener al menos 8 caracteres, una letra mayúscula, una letra minúscula, un número y un carácter especial')
        return v


class Usuario(UsuarioBase):
    id: int
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    is_active: bool
    is_admin: bool
    fecha_creacion: datetime
    ultimo_login: Optional[datetime] = None

    class Config:
        from_attributes = True