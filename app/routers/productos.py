from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.database import get_db
from ..core.config import settings
from ..core.security import get_current_admin_user
from ..schemas.producto import Producto, ProductoCreate, ProductoUpdate
from ..models.producto import Producto as ProductoModel
from ..models.categoria import Categoria as CategoriaModel
from ..exceptions import NotFoundException, BadRequestException

# Limiter para rate limiting
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/productos",
    tags=["productos"]
)


@router.post("/", response_model=Producto, status_code=201)
async def crear_producto(
        producto: ProductoCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """
    Crea un nuevo producto (solo administradores).

    - **nombre**: Nombre del producto (3-100 caracteres)
    - **descripcion**: Descripción del producto (opcional, máx 1000 caracteres)
    - **precio**: Precio del producto (entero positivo)
    - **disponible**: Estado de disponibilidad (por defecto: True)
    - **stock**: Cantidad disponible (por defecto: 0)
    - **categoria_id**: ID de la categoría a la que pertenece el producto
    """
    # Verificar si la categoría existe
    categoria = db.query(CategoriaModel).filter(CategoriaModel.id == producto.categoria_id).first()
    if not categoria:
        raise BadRequestException(f"No existe categoría con ID {producto.categoria_id}")

    # Crear producto
    db_producto = ProductoModel(**producto.dict())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)

    return db_producto


@router.get("/", response_model=List[Producto])
@limiter.limit("30/minute")
async def leer_productos(
        request: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(settings.DEFAULT_LIMIT, le=settings.MAX_LIMIT),
        db: Session = Depends(get_db)
):
    """
    Obtiene la lista de productos.

    Este endpoint es público y permite obtener todos los productos.
    Soporta paginación con los parámetros skip y limit.
    """
    productos = db.query(ProductoModel).order_by(ProductoModel.id).offset(skip).limit(limit).all()
    return productos


@router.get("/{producto_id}", response_model=Producto)
async def leer_producto(
        producto_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene la información de un producto específico.

    Este endpoint es público y permite obtener la información de un producto
    por su ID.
    """
    db_producto = db.query(ProductoModel).filter(ProductoModel.id == producto_id).first()
    if db_producto is None:
        raise NotFoundException("Producto no encontrado")

    return db_producto


@router.put("/{producto_id}", response_model=Producto)
async def actualizar_producto(
        producto_id: int,
        producto: ProductoUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """
    Actualiza un producto existente (solo administradores).

    Permite actualizar cualquiera de los campos del producto:
    - **nombre**: Nombre del producto (3-100 caracteres)
    - **descripcion**: Descripción del producto (máx 1000 caracteres)
    - **precio**: Precio del producto (entero positivo)
    - **disponible**: Estado de disponibilidad
    - **stock**: Cantidad disponible
    - **categoria_id**: ID de la categoría a la que pertenece el producto
    """
    # Verificar si el producto existe
    db_producto = db.query(ProductoModel).filter(ProductoModel.id == producto_id).first()
    if db_producto is None:
        raise NotFoundException("Producto no encontrado")

    # Verificar si la categoría existe si se está actualizando
    if producto.categoria_id is not None:
        categoria = db.query(CategoriaModel).filter(CategoriaModel.id == producto.categoria_id).first()
        if not categoria:
            raise BadRequestException(f"No existe categoría con ID {producto.categoria_id}")

    # Actualizar los campos proporcionados
    update_data = producto.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_producto, key, value)

    db.commit()
    db.refresh(db_producto)

    return db_producto


@router.delete("/{producto_id}", response_model=Producto)
async def eliminar_producto(
        producto_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """
    Elimina un producto (solo administradores).

    Este endpoint elimina un producto por su ID.
    """
    db_producto = db.query(ProductoModel).filter(ProductoModel.id == producto_id).first()
    if db_producto is None:
        raise NotFoundException("Producto no encontrado")

    db.delete(db_producto)
    db.commit()

    return db_producto