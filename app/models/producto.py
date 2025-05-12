from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel
from ..core.database import Base

class Producto(Base, BaseModel):
    __tablename__ = "productos"

    nombre = Column(String(100), nullable=False, index=True)
    descripcion = Column(String(1000))
    precio = Column(Integer, nullable=False)
    disponible = Column(Boolean, default=True)
    stock = Column(Integer, default=0)
    categoria_id = Column(Integer, ForeignKey("categorias.id", ondelete="CASCADE"))

    categoria = relationship("Categoria", back_populates="productos")