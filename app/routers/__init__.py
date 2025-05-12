from .auth import router as auth_router
from .usuarios import router as usuarios_router
from .categorias import router as categorias_router
from .productos import router as productos_router

# Exportar los routers para que sean fácilmente importables
router = [auth_router, usuarios_router, categorias_router, productos_router]

__all__ = [
    "auth",
    "usuarios",
    "categorias",
    "productos"
]