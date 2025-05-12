from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=50,
                        description="Nombre de la categoría (2-50 caracteres)")

    @validator('nombre')
    def nombre_no_contiene_caracteres_especiales(cls, v):
        if not v.replace(' ', '').isalnum():
            raise ValueError('El nombre de la categoría no debe contener caracteres especiales')
        return v


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)

    @validator('nombre')
    def nombre_no_contiene_caracteres_especiales(cls, v):
        if v is not None and not v.replace(' ', '').isalnum():
            raise ValueError('El nombre de la categoría no debe contener caracteres especiales')
        return v


class Categoria(CategoriaBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True