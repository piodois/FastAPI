from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from typing import Dict, Any

from .core.config import settings  # Nota el punto antes de core
from .core.database import engine
from .models import Base
from .exceptions import setup_exception_handlers
from .routers import auth, usuarios, categorias, productos

# Inicialización de la base de datos
Base.metadata.create_all(bind=engine)

# Limiter para rate limiting
limiter = Limiter(key_func=get_remote_address)

# Descripción de la API
descripcion_api = """
# API de Gestión de Productos y Categorías

Esta API permite gestionar productos y categorías con una autenticación segura.

## Características

* **Autenticación**: Login y registro de usuarios con JWT
* **Usuarios**: Gestión de usuarios con roles (admin/normal)
* **Categorías**: CRUD completo para categorías
* **Productos**: CRUD completo para productos con filtrado avanzado

## Notas de Seguridad

* Todas las contraseñas son hasheadas antes de almacenarse
* Los tokens JWT expiran después de 30 minutos
* Las operaciones de administración requieren privilegios de administrador
"""

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description=descripcion_api,
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


# Middleware para logging y medición de rendimiento
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Configurar manejadores de excepciones
setup_exception_handlers(app, debug=settings.DEBUG)

# Configurar rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Manejador personalizado para errores de validación
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        error_detail = {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"]
        }
        errors.append(error_detail)

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Error de validación en los datos enviados",
            "errors": errors
        }
    )


# Incluir routers
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(categorias.router)
app.include_router(productos.router)


# Página de bienvenida en la ruta principal
@app.get("/", response_class=HTMLResponse)
@limiter.limit("10/minute")
async def root(request: Request):
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>API FastAPI con SQL Server</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    margin: 0;
                    padding: 0;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                }
                .container {
                    background-color: white;
                    border-radius: 12px;
                    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
                    padding: 2.5rem;
                    max-width: 800px;
                    width: 90%;
                }
                h1 {
                    color: #2c3e50;
                    margin-bottom: 1.5rem;
                    font-size: 2.2rem;
                    border-bottom: 2px solid #eaeaea;
                    padding-bottom: 0.8rem;
                }
                p {
                    color: #555;
                    line-height: 1.7;
                    font-size: 1.1rem;
                    margin-bottom: 1.5rem;
                }
                .features {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 1.2rem;
                    margin-bottom: 1.5rem;
                }
                .features h2 {
                    color: #3498db;
                    margin-top: 0;
                    font-size: 1.4rem;
                }
                .features ul {
                    padding-left: 1.2rem;
                }
                .features li {
                    margin-bottom: 0.5rem;
                    color: #555;
                }
                .buttons {
                    margin-top: 2rem;
                    display: flex;
                    gap: 1rem;
                    flex-wrap: wrap;
                }
                .button {
                    display: inline-block;
                    background-color: #3498db;
                    color: white;
                    padding: 0.8rem 1.8rem;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: bold;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 6px rgba(50, 50, 93, 0.11), 0 1px 3px rgba(0, 0, 0, 0.08);
                    border: none;
                    cursor: pointer;
                }
                .button:hover {
                    background-color: #2980b9;
                    transform: translateY(-2px);
                    box-shadow: 0 7px 14px rgba(50, 50, 93, 0.1), 0 3px 6px rgba(0, 0, 0, 0.08);
                }
                .button.secondary {
                    background-color: #2ecc71;
                }
                .button.secondary:hover {
                    background-color: #27ae60;
                }
                .version {
                    margin-top: 2rem;
                    font-size: 0.9rem;
                    color: #7f8c8d;
                    text-align: center;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>API FastAPI con SQL Server</h1>
                <p>Bienvenido a la API de gestión de productos y categorías. Esta API proporciona endpoints seguros y robustos para la creación, lectura, actualización y eliminación de registros.</p>

                <div class="features">
                    <h2>Características:</h2>
                    <ul>
                        <li>Autenticación JWT segura con roles de usuario</li>
                        <li>Validación avanzada de datos de entrada</li>
                        <li>Manejo robusto de errores y excepciones</li>
                        <li>Documentación interactiva completa</li>
                        <li>Filtrado dinámico de productos</li>
                    </ul>
                </div>

                <p>Utiliza la documentación interactiva para probar los diferentes endpoints disponibles en la API.</p>

                <div class="buttons">
                    <a href="/docs" class="button">Documentación Swagger</a>
                    <a href="/redoc" class="button secondary">Documentación ReDoc</a>
                </div>

                <div class="version">
                    <p>Versión 1.0.0</p>
                </div>
            </div>
        </body>
    </html>
    """
    return html_content


# Endpoint para verificar estado de la API
@app.get("/health", tags=["sistema"])
@limiter.limit("30/minute")
async def health_check(request: Request) -> Dict[str, Any]:
    """
    Comprueba el estado de salud de la API.
    """
    return {
        "status": "online",
        "version": "1.0.0",
        "timestamp": time.time()
    }


# Si se ejecuta directamente
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)