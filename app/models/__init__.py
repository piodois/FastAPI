# app/models/__init__.py
from .usuario import Usuario
from .categoria import Categoria
from .producto import Producto
from .registroingreso import RegistroIngreso
from ..core.database import Base

__all__ = ["Usuario", "Categoria", "Producto", "RegistroIngreso", "Base"]