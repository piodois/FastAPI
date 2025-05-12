from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.database import get_db
from ..core.config import settings
from ..core.security import get_current_admin_user
from ..schemas.categoria import Categoria, CategoriaCreate, CategoriaUpdate
from ..models.categoria import Categoria as CategoriaModel
from ..exceptions import NotFoundException, BadRequestException, ConflictException

# Limiter para rate limiting
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/categorias",
    tags=["categorías"]
)


@router.post("/", response_model=Categoria, status_code=201)
async def crear_categoria(
        categoria: CategoriaCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """
    Crea una nueva categoría (solo administradores).

    - **nombre**: Nombre de la categoría (único, 2-50 caracteres)
    """
    # Verificar si ya existe una categoría con ese nombre
    db_categoria = db.query(CategoriaModel).filter(CategoriaModel.nombre == categoria.nombre).first()
    if db_categoria:
        raise ConflictException("Ya existe una categoría con ese nombre")

    # Crear categoría
    db_categoria = CategoriaModel(nombre=categoria.nombre)
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)

    return db_categoria


@router.get("/", response_model=List[Categoria])
@limiter.limit("30/minute")
async def leer_categorias(
        request: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(settings.DEFAULT_LIMIT, le=settings.MAX_LIMIT),
        db: Session = Depends(get_db)
):
    """
    Obtiene la lista de categorías.

    Este endpoint es público y permite obtener todas las categorías.
    Soporta paginación con los parámetros skip y limit.
    """
    categorias = db.query(CategoriaModel).order_by(CategoriaModel.id).offset(skip).limit(limit).all()
    return categorias


@router.get("/{categoria_id}", response_model=Categoria)
async def leer_categoria(
        categoria_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene la información de una categoría específica.

    Este endpoint es público y permite obtener la información de una categoría
    por su ID.
    """
    db_categoria = db.query(CategoriaModel).filter(CategoriaModel.id == categoria_id).first()
    if db_categoria is None:
        raise NotFoundException("Categoría no encontrada")

    return db_categoria


@router.put("/{categoria_id}", response_model=Categoria)
async def actualizar_categoria(
        categoria_id: int,
        categoria: CategoriaUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """
    Actualiza una categoría existente (solo administradores).

    - **nombre**: Nuevo nombre de la categoría (2-50 caracteres)
    """
    # Verificar si la categoría existe
    db_categoria = db.query(CategoriaModel).filter(CategoriaModel.id == categoria_id).first()
    if db_categoria is None:
        raise NotFoundException("Categoría no encontrada")

    # Verificar si el nuevo nombre ya existe en otra categoría
    if categoria.nombre and categoria.nombre != db_categoria.nombre:
        exists = db.query(CategoriaModel).filter(CategoriaModel.nombre == categoria.nombre).first()
        if exists:
            raise ConflictException("Ya existe una categoría con ese nombre")

    # Actualizar categoría
    if categoria.nombre:
        db_categoria.nombre = categoria.nombre

    db.commit()
    db.refresh(db_categoria)

    return db_categoria


@router.delete("/{categoria_id}", response_model=Categoria)
async def eliminar_categoria(
        categoria_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """
    Elimina una categoría (solo administradores).

    Este endpoint elimina la categoría y todos los productos asociados a ella
    (si la relación tiene cascade delete).
    """
    db_categoria = db.query(CategoriaModel).filter(CategoriaModel.id == categoria_id).first()
    if db_categoria is None:
        raise NotFoundException("Categoría no encontrada")

    db.delete(db_categoria)
    db.commit()

    return db_categoria