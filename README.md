# API FastAPI con SQL Server

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![SQL Server](https://img.shields.io/badge/Microsoft%20SQL%20Server-CC2927?style=for-the-badge&logo=microsoft%20sql%20server&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

## Descripción

API RESTful desarrollada con FastAPI y SQL Server para la gestión de productos y categorías con autenticación JWT. Esta API implementa un CRUD completo con validaciones avanzadas, manejo de excepciones personalizado, límites de tasa (rate limiting) y documentación interactiva.

## Características principales

- **Autenticación y autorización** basada en JWT con roles de usuario (admin/normal)
- **Gestión de usuarios** con validación de contraseñas seguras
- **CRUD completo** para productos y categorías
- **Filtrado avanzado** de productos por múltiples criterios
- **Validación de datos** con Pydantic y validadores personalizados
- **Manejo robusto de excepciones** con mensajes descriptivos
- **Límites de tasa (rate limiting)** para prevenir abusos
- **Documentación interactiva** con Swagger y ReDoc

## Estructura del proyecto

```
app/
│
├── core/                    # Configuración central y componentes esenciales
│   ├── __init__.py
│   ├── config.py            # Variables de configuración
│   ├── database.py          # Configuración de la base de datos
│   └── security.py          # Funciones de seguridad y autenticación
│
├── exceptions/              # Manejo de excepciones personalizadas
│   ├── __init__.py
│   ├── handlers.py          # Manejadores de excepciones
│   └── http_exceptions.py   # Clases de excepciones HTTP
│
├── models/                  # Modelos SQLAlchemy para la base de datos
│   ├── __init__.py
│   ├── base.py              # Modelo base con campos comunes
│   ├── categoria.py         # Modelo de categoría
│   ├── producto.py          # Modelo de producto
│   └── usuario.py           # Modelo de usuario
│
├── routers/                 # Rutas API agrupadas por recursos
│   ├── __init__.py
│   ├── auth.py              # Endpoints de autenticación
│   ├── categorias.py        # Endpoints de categorías
│   ├── productos.py         # Endpoints de productos
│   └── usuarios.py          # Endpoints de usuarios
│
├── schemas/                 # Esquemas Pydantic para validación
│   ├── __init__.py
│   ├── categoria.py         # Esquemas de categoría
│   ├── producto.py          # Esquemas de producto
│   ├── token.py             # Esquemas de tokens
│   └── usuario.py           # Esquemas de usuario
│
├── utils/                   # Funciones de utilidad
│   ├── __init__.py
│   └── validators.py        # Validadores personalizados
│
├── __init__.py
├── main.py                  # Punto de entrada de la aplicación
└── requirements.txt         # Dependencias del proyecto
```

## Requisitos

- Python 3.8+
- SQL Server
- Controlador ODBC para SQL Server

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone https://github.com/piodois/FastAPI.git
   cd api-fastapi-sqlserver
   ```

2. Crear un entorno virtual e instalar dependencias:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Configurar variables de entorno:
   - Copia el archivo `.env.example` a `.env`
   - Edita el archivo `.env` con los valores apropiados para tu entorno

## Configuración

El archivo `.env` debe contener:

```
# Configuración de la base de datos
DB_HOST=localhost
DB_PORT=1433
DB_NAME=nombre_base_datos
DB_USER=usuario
DB_PASSWORD=contraseña
DB_TRUSTED_CONNECTION=False

# Configuración de seguridad
SECRET_KEY=clave_secreta_para_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Configuración de la aplicación
DEBUG=True
BACKEND_CORS_ORIGINS=["http://localhost", "http://localhost:4200"]

# Límites y paginación
DEFAULT_LIMIT=100
MAX_LIMIT=1000
```

## Uso

### Iniciar el servidor

```bash
uvicorn app.main:app --reload
```

El servidor se iniciará en `http://localhost:8000`

### Documentación de la API

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Ejemplos de uso

#### Autenticación

```bash
# Registro de usuario
curl -X 'POST' \
  'http://localhost:8000/api/v1/auth/registro' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "usuario@ejemplo.com",
  "username": "usuario1",
  "password": "Contraseña123!",
  "nombre": "Usuario",
  "apellido": "Ejemplo"
}'

# Iniciar sesión
curl -X 'POST' \
  'http://localhost:8000/api/v1/auth/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=usuario1&password=Contraseña123!'
```

#### Operaciones CRUD

```bash
# Crear una categoría (requiere autenticación como admin)
curl -X 'POST' \
  'http://localhost:8000/api/v1/categorias/' \
  -H 'Authorization: Bearer TU_TOKEN_JWT' \
  -H 'Content-Type: application/json' \
  -d '{
  "nombre": "Electrónica"
}'

# Listar productos
curl -X 'GET' \
  'http://localhost:8000/api/v1/productos/'

# Filtrar productos
curl -X 'GET' \
  'http://localhost:8000/api/v1/productos/filtrar/?precio_min=1000&disponible=true&categoria_id=1'
```

## Endpoints principales

### Autenticación
- `POST /api/v1/auth/login`: Iniciar sesión y obtener token JWT
- `POST /api/v1/auth/registro`: Registrar un nuevo usuario

### Usuarios
- `GET /api/v1/usuarios/me`: Obtener datos del usuario actual
- `PUT /api/v1/usuarios/me`: Actualizar datos del usuario actual
- `GET /api/v1/usuarios/`: Listar usuarios (solo admin)
- `POST /api/v1/usuarios/`: Crear un nuevo usuario (solo admin)
- `PUT /api/v1/usuarios/{id}`: Actualizar un usuario (solo admin)
- `DELETE /api/v1/usuarios/{id}`: Eliminar un usuario (solo admin)

### Categorías
- `GET /api/v1/categorias/`: Listar categorías
- `GET /api/v1/categorias/{id}`: Obtener una categoría
- `POST /api/v1/categorias/`: Crear una categoría (solo admin)
- `PUT /api/v1/categorias/{id}`: Actualizar una categoría (solo admin)
- `DELETE /api/v1/categorias/{id}`: Eliminar una categoría (solo admin)

### Productos
- `GET /api/v1/productos/`: Listar productos
- `GET /api/v1/productos/{id}`: Obtener un producto
- `POST /api/v1/productos/`: Crear un producto (solo admin)
- `PUT /api/v1/productos/{id}`: Actualizar un producto (solo admin)
- `DELETE /api/v1/productos/{id}`: Eliminar un producto (solo admin)
- `GET /api/v1/productos/filtrar/`: Filtrar productos por diversos criterios
- `GET /api/v1/productos/buscar/{texto}`: Buscar productos por texto
- `GET /api/v1/productos/destacados/`: Obtener productos destacados
- `GET /api/v1/productos/categoria/{id}/productos`: Obtener productos por categoría

## Seguridad

- Todas las contraseñas se almacenan hasheadas con bcrypt
- Autenticación mediante tokens JWT con expiración
- Validación de fortaleza de contraseñas
- Protección contra ataques de fuerza bruta mediante rate limiting
- Validación de datos de entrada con Pydantic
- Manejo de errores personalizado para evitar fugas de información

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Si tienes preguntas o sugerencias, no dudes en contactarme:

- Correo electrónico: tu.email@ejemplo.com
- GitHub: [tu-usuario](https://github.com/piodois)

---

Desarrollado con ❤️ usando FastAPI y SQL Server.
