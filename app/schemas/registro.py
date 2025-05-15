# app/schemas/registro.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RegistroBase(BaseModel):
    documento: int = Field(..., gt=0, description="Número de documento (entero positivo)")
    nombre: str = Field(..., min_length=2, max_length=100, description="Nombre asociado al registro")

class RegistroCreate(RegistroBase):
    pass

class RegistroUpdate(BaseModel):
    documento: Optional[int] = Field(None, gt=0)
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)

class Registro(RegistroBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True