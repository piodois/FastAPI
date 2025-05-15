# app/routers/registros.py
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.database import get_db
from ..core.config import settings
from ..core.security import get_current_admin_user
from ..schemas.registro import Registro, RegistroCreate, RegistroUpdate
from ..models.registro import Registro as RegistroModel
from ..exceptions import NotFoundException, BadRequestException

# Limiter para rate limiting
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/registros",
    tags=["registros"]
)

@router.post("/", response_model=Registro, status_code=201)
async def crear_registro(
        registro: RegistroCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """
    Crea un nuevo registro (solo administradores).

    - **documento**: Número de documento (entero positivo)
    - **nombre**: Nombre asociado al registro (2-100 caracteres)
    """
    # Crear registro
    db_registro = RegistroModel(**registro.dict())
    db.add(db_registro)
    db.commit()
    db.refresh(db_registro)

    return db_registro

@router.get("/", response_model=List[Registro])
@limiter.limit("30/minute")
async def leer_registros(
        request: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(settings.DEFAULT_LIMIT, le=settings.MAX_LIMIT),
        db: Session = Depends(get_db)
):
    """
    Obtiene la lista de registros.

    Este endpoint es público y permite obtener todos los registros.
    Soporta paginación con los parámetros skip y limit.
    """
    registros = db.query(RegistroModel).order_by(RegistroModel.id).offset(skip).limit(limit).all()
    return registros

@router.get("/{registro_id}", response_model=Registro)
async def leer_registro(
        registro_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene la información de un registro específico.

    Este endpoint es público y permite obtener la información de un registro
    por su ID.
    """
    db_registro = db.query(RegistroModel).filter(RegistroModel.id == registro_id).first()
    if db_registro is None:
        raise NotFoundException("Registro no encontrado")

    return db_registro

@router.put("/{registro_id}", response_model=Registro)
async def actualizar_registro(
        registro_id: int,
        registro: RegistroUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """
    Actualiza un registro existente (solo administradores).

    Permite actualizar cualquiera de los campos del registro:
    - **documento**: Número de documento (entero positivo)
    - **nombre**: Nombre asociado al registro (2-100 caracteres)
    """
    # Verificar si el registro existe
    db_registro = db.query(RegistroModel).filter(RegistroModel.id == registro_id).first()
    if db_registro is None:
        raise NotFoundException("Registro no encontrado")

    # Actualizar los campos proporcionados
    update_data = registro.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_registro, key, value)

    db.commit()
    db.refresh(db_registro)

    return db_registro

@router.delete("/{registro_id}", response_model=Registro)
async def eliminar_registro(
        registro_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """
    Elimina un registro (solo administradores).

    Este endpoint elimina un registro por su ID.
    """
    db_registro = db.query(RegistroModel).filter(RegistroModel.id == registro_id).first()
    if db_registro is None:
        raise NotFoundException("Registro no encontrado")

    db.delete(db_registro)
    db.commit()

    return db_registro