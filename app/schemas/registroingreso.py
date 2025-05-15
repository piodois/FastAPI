# app/schemas/registroingreso.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class RegistroIngresoBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100,
                        description="Nombre del registro de ingreso")
    descripcion: Optional[str] = Field(None, max_length=500,
                                       description="Descripción del registro")
    cantidad: int = Field(0, ge=0, description="Cantidad del registro")


class RegistroIngresoCreate(RegistroIngresoBase):
    pass


class RegistroIngresoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    cantidad: Optional[int] = Field(None, ge=0)


class RegistroIngreso(RegistroIngresoBase):
    id: int
    fecha_creacion: datetime
    fecha_ingreso: Optional[datetime] = None

    class Config:
        from_attributes = True