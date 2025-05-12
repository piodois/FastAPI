from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel
from ..core.database import Base


class Usuario(Base, BaseModel):
    __tablename__ = "usuarios"

    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    nombre = Column(String(100))
    apellido = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    ultimo_login = Column(DateTime(timezone=True), nullable=True)

    # Relación con otros modelos si es necesario
    # productos = relationship("Producto", back_populates="usuario")