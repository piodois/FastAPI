from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import BaseModel
from ..core.database import Base

class Categoria(Base, BaseModel):
    __tablename__ = "categorias"

    nombre = Column(String(50), nullable=False, unique=True)

    productos = relationship("Producto", back_populates="categoria", cascade="all, delete-orphan")