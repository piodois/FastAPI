# app/models/registro.py
from sqlalchemy import Column, String, Integer
from .base import BaseModel
from ..core.database import Base

class Registro(Base, BaseModel):
    __tablename__ = "registros"

    documento = Column(Integer, nullable=False)
    nombre = Column(String(100), nullable=False)