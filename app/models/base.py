from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from ..core.database import Base

class BaseModel:
    id = Column(Integer, primary_key=True, index=True)
    fecha_creacion = Column(DateTime(timezone=True), server_default=func.now())