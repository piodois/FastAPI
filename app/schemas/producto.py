from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from .categoria import Categoria


class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=3, max_length=100,
                        description="Nombre del producto (3-100 caracteres)")
    descripcion: Optional[str] = Field(None, max_length=1000,
                                       description="Descripción del producto (máximo 1000 caracteres)")
    precio: int = Field(..., gt=0, lt=10000000,
                        description="Precio del producto (mayor que 0, menor que 10,000,000)")
    disponible: bool = True
    stock: int = Field(0, ge=0, description="Cantidad disponible en inventario")
    categoria_id: int = Field(..., gt=0, description="ID de la categoría")


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=1000)
    precio: Optional[int] = Field(None, gt=0, lt=10000000)
    disponible: Optional[bool] = None
    stock: Optional[int] = Field(None, ge=0)
    categoria_id: Optional[int] = Field(None, gt=0)


class Producto(ProductoBase):
    id: int
    fecha_creacion: datetime
    categoria: Categoria

    class Config:
        from_attributes = True


class ProductoFilter(BaseModel):
    nombre: Optional[str] = None
    precio_min: Optional[int] = Field(None, ge=0)
    precio_max: Optional[int] = Field(None, gt=0)
    disponible: Optional[bool] = None
    stock_min: Optional[int] = Field(None, ge=0)
    categoria_id: Optional[int] = Field(None, gt=0)

    @validator('precio_max')
    def precio_max_mayor_que_precio_min(cls, v, values):
        if v is not None and 'precio_min' in values and values['precio_min'] is not None:
            if v <= values['precio_min']:
                raise ValueError('El precio máximo debe ser mayor que el precio mínimo')
        return v