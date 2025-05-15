# app/routers/registrosdeingreso.py
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.database import get_db
from ..core.config import settings
from ..core.security import get_current_admin_user
from ..schemas.registroingreso import RegistroIngreso, RegistroIngresoCreate, RegistroIngresoUpdate
from ..models.registroingreso import RegistroIngreso as RegistroIngresoModel
from ..exceptions import NotFoundException, BadRequestException

# Limiter para rate limiting
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/registros-ingreso",
    tags=["registros de ingreso"]
)


@router.get("/", response_model=List[RegistroIngreso])
@limiter.limit("30/minute")
async def leer_registros(
        request: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(settings.DEFAULT_LIMIT, le=settings.MAX_LIMIT),
        db: Session = Depends(get_db)
):
    """
    Obtiene la lista de registros de ingreso.

    Este endpoint permite obtener todos los registros de ingreso.
    Soporta paginación con los parámetros skip y limit.
    """
    registros = db.query(RegistroIngresoModel).order_by(RegistroIngresoModel.id).offset(skip).limit(limit).all()
    return registros


@router.get("/{registro_id}", response_model=RegistroIngreso)
async def leer_registro(
        registro_id: int,
        db: Session = Depends(get_db)
):
    """
    Obtiene la información de un registro de ingreso específico.

    Este endpoint permite obtener la información de un registro
    por su ID.
    """
    db_registro = db.query(RegistroIngresoModel).filter(RegistroIngresoModel.id == registro_id).first()
    if db_registro is None:
        raise NotFoundException("Registro no encontrado")

    return db_registro


@router.post("/", response_model=RegistroIngreso, status_code=201)
async def crear_registro(
        registro: RegistroIngresoCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """
    Crea un nuevo registro de ingreso.
    """
    # Crear registro
    db_registro = RegistroIngresoModel(**registro.dict())
    db.add(db_registro)
    db.commit()
    db.refresh(db_registro)

    return db_registro


@router.put("/{registro_id}", response_model=RegistroIngreso)
async def actualizar_registro(
        registro_id: int,
        registro: RegistroIngresoUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """
    Actualiza un registro de ingreso existente.
    """
    # Verificar si el registro existe
    db_registro = db.query(RegistroIngresoModel).filter(RegistroIngresoModel.id == registro_id).first()
    if db_registro is None:
        raise NotFoundException("Registro no encontrado")

    # Actualizar los campos proporcionados
    update_data = registro.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_registro, key, value)

    db.commit()
    db.refresh(db_registro)

    return db_registro


@router.delete("/{registro_id}", response_model=RegistroIngreso)
async def eliminar_registro(
        registro_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_admin_user)
):
    """
    Elimina un registro de ingreso.
    """
    db_registro = db.query(RegistroIngresoModel).filter(RegistroIngresoModel.id == registro_id).first()
    if db_registro is None:
        raise NotFoundException("Registro no encontrado")

    db.delete(db_registro)
    db.commit()

    return db_registro