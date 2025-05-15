# app/models/registroingreso.py
from sqlalchemy import Column, String, Integer, DateTime
from .base import BaseModel
from ..core.database import Base


class RegistroIngreso(Base, BaseModel):
    __tablename__ = "registrosdeingreso"

    # Estos campos deberán ajustarse según la estructura real de la tabla
    # Cuando recibas las columnas y tipos de datos exactos, deberás actualizarlos
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500), nullable=True)
    cantidad = Column(Integer, default=0)
    fecha_ingreso = Column(DateTime(timezone=True), nullable=True)