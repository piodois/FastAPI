# app/__init__.py

# Importar las funciones y módulos principales
from .core.config import settings
from .core.database import get_db, Base, engine
from .exceptions import setup_exception_handlers

# Exportar componentes importantes
__all__ = [
    "settings",
    "get_db",
    "Base",
    "engine",
    "setup_exception_handlers"
]

# Versión de la aplicación
__version__ = "1.0.0"

# Información sobre la aplicación
APP_NAME = settings.PROJECT_NAME
API_V1_STR = settings.API_V1_STR


# Configurar rutas de las aplicaciones
def get_app_routes():
    """Obtener todas las rutas de la aplicación."""
    return {
        "auth": f"{API_V1_STR}/auth",
        "usuarios": f"{API_V1_STR}/usuarios",
        "categorias": f"{API_V1_STR}/categorias",
        "productos": f"{API_V1_STR}/productos"
    }


# Esta función puede ser llamada desde scripts externos
def create_app():
    """Crear y configurar la aplicación FastAPI."""
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from .routers import auth, usuarios, categorias, productos
    from .exceptions import setup_exception_handlers

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=__version__,
        description="API para gestión de productos y categorías con autenticación segura.",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configuración de CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Configurar manejadores de excepciones
    setup_exception_handlers(app, debug=settings.DEBUG)

    # Incluir routers
    app.include_router(auth.router)
    app.include_router(usuarios.router)
    app.include_router(categorias.router)
    app.include_router(productos.router)

    return app


# Inicialización automática de tablas al importar el módulo
def init_db():
    """Inicializar la base de datos si es necesario."""
    try:
        Base.metadata.create_all(bind=engine)
        print("Base de datos inicializada correctamente.")
    except Exception as e:
        print(f"Error al inicializar la base de datos: {e}")


# Esto permite un patrón común en Python donde app/__init__.py
# realiza alguna configuración automática al importar el paquete
if settings.DEBUG:
    print(f"Iniciando aplicación {APP_NAME} en modo DEBUG")
    print(f"Versión de la API: {__version__}")
    print(f"Rutas disponibles: {get_app_routes()}")