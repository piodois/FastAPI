from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.database import get_db
from ..core.config import settings
from ..core.security import get_current_admin_user
from ..schemas.producto import Producto, ProductoCreate, ProductoUpdate, ProductoFilter
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


@router.get("/filtrar/", response_model=List[Producto])
@limiter.limit("20/minute")
async def filtrar_productos(
        request: Request,
        nombre: Optional[str] = None,
        precio_min: Optional[int] = Query(None, ge=0),
        precio_max: Optional[int] = Query(None, gt=0),
        disponible: Optional[bool] = None,
        stock_min: Optional[int] = Query(None, ge=0),
        categoria_id: Optional[int] = Query(None, gt=0),
        ordernar_por: Optional[str] = Query(None, regex="^(nombre|precio|stock|fecha_creacion)$"),
        orden: Optional[str] = Query("asc", regex="^(asc|desc)$"),
        skip: int = Query(0, ge=0),
        limit: int = Query(settings.DEFAULT_LIMIT, le=settings.MAX_LIMIT),
        db: Session = Depends(get_db)
):
    """
    Filtra productos por diversos criterios.

    Este endpoint es público y permite obtener productos filtrados por:
    - **nombre**: Busca coincidencias parciales en el nombre
    - **precio_min**: Precio mínimo
    - **precio_max**: Precio máximo
    - **disponible**: Estado de disponibilidad
    - **stock_min**: Stock mínimo disponible
    - **categoria_id**: ID de la categoría

    También permite ordenar los resultados por diversos campos:
    - **ordernar_por**: Campo por el que ordenar (nombre, precio, stock, fecha_creacion)
    - **orden**: Dirección del ordenamiento (asc, desc)

    Soporta paginación con los parámetros skip y limit.
    """
    # Construir la consulta base
    query = db.query(ProductoModel)

    # Aplicar filtros si se proporcionan
    if nombre:
        query = query.filter(ProductoModel.nombre.ilike(f"%{nombre}%"))

    if precio_min is not None:
        query = query.filter(ProductoModel.precio >= precio_min)

    if precio_max is not None:
        query = query.filter(ProductoModel.precio <= precio_max)

    if disponible is not None:
        query = query.filter(ProductoModel.disponible == disponible)

    if stock_min is not None:
        query = query.filter(ProductoModel.stock >= stock_min)

    if categoria_id is not None:
        query = query.filter(ProductoModel.categoria_id == categoria_id)

    # Aplicar ordenamiento
    if ordernar_por:
        order_column = getattr(ProductoModel, ordernar_por)
        if orden == "desc":
            order_column = order_column.desc()
        query = query.order_by(order_column)
    else:
        # Ordenamiento por defecto
        query = query.order_by(ProductoModel.id)

    # Aplicar paginación
    productos = query.offset(skip).limit(limit).all()

    return productos


@router.get("/buscar/{texto}", response_model=List[Producto])
@limiter.limit("15/minute")
async def buscar_productos(
        request: Request,
        texto: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(settings.DEFAULT_LIMIT, le=settings.MAX_LIMIT),
        db: Session = Depends(get_db)
):
    """
    Busca productos por texto en nombre y descripción.

    Este endpoint es público y permite buscar productos cuyo nombre o descripción
    contengan el texto proporcionado.

    Soporta paginación con los parámetros skip y limit.
    """
    if len(texto) < 3:
        raise BadRequestException("El texto de búsqueda debe tener al menos 3 caracteres")

    # Buscar en nombre y descripción
    productos = db.query(ProductoModel).filter(
        or_(
            ProductoModel.nombre.ilike(f"%{texto}%"),
            ProductoModel.descripcion.ilike(f"%{texto}%")
        )
    ).order_by(ProductoModel.id).offset(skip).limit(limit).all()

    return productos


@router.get("/categoria/{categoria_id}/productos", response_model=List[Producto])
async def productos_por_categoria(
        categoria_id: int,
        disponible: Optional[bool] = None,
        skip: int = Query(0, ge=0),
        limit: int = Query(settings.DEFAULT_LIMIT, le=settings.MAX_LIMIT),
        db: Session = Depends(get_db)
):
    """
    Obtiene los productos de una categoría específica.

    Este endpoint es público y permite obtener todos los productos
    que pertenecen a una categoría determinada.

    Opcionalmente puede filtrar por disponibilidad y soporta paginación.
    """
    # Verificar si la categoría existe
    categoria = db.query(CategoriaModel).filter(CategoriaModel.id == categoria_id).first()
    if not categoria:
        raise NotFoundException(f"No existe categoría con ID {categoria_id}")

    # Construir la consulta
    query = db.query(ProductoModel).filter(ProductoModel.categoria_id == categoria_id)

    # Aplicar filtro de disponibilidad si se proporciona
    if disponible is not None:
        query = query.filter(ProductoModel.disponible == disponible)

    # Aplicar paginación
    productos = query.order_by(ProductoModel.nombre).offset(skip).limit(limit).all()

    return productos


@router.get("/destacados/", response_model=List[Producto])
async def productos_destacados(
        limite: int = Query(10, ge=1, le=50),
        db: Session = Depends(get_db)
):
    """
    Obtiene una lista de productos destacados.

    Este endpoint es público y devuelve los productos disponibles
    con mayor stock, que podrían considerarse destacados.
    """
    productos = db.query(ProductoModel).filter(
        ProductoModel.disponible == True
    ).order_by(ProductoModel.stock.desc()).limit(limite).all()

    return productos