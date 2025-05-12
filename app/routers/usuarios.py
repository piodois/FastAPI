from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.database import get_db
from ..core.config import settings
from ..core.security import get_current_active_user, get_current_admin_user, get_password_hash
from ..schemas.usuario import Usuario, UsuarioCreate, UsuarioUpdate
from ..models.usuario import Usuario as UsuarioModel
from ..exceptions import NotFoundException, BadRequestException, ForbiddenException

# Limiter para rate limiting
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/usuarios",
    tags=["usuarios"]
)


@router.post("/", response_model=Usuario, status_code=201)
async def crear_usuario(
        usuario: UsuarioCreate,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_admin_user)
):
    """
    Crea un nuevo usuario (solo administradores).

    Este endpoint permite a los administradores crear nuevos usuarios,
    incluyendo la posibilidad de asignar permisos de administrador.
    """
    # Verificar si el email ya existe
    if db.query(UsuarioModel).filter(UsuarioModel.email == usuario.email).first():
        raise BadRequestException("El correo electrónico ya está registrado")

    # Verificar si el username ya existe
    if db.query(UsuarioModel).filter(UsuarioModel.username == usuario.username).first():
        raise BadRequestException("El nombre de usuario ya está en uso")

    # Crear usuario
    hashed_password = get_password_hash(usuario.password)
    db_usuario = UsuarioModel(
        email=usuario.email,
        username=usuario.username,
        hashed_password=hashed_password,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        is_active=usuario.is_active,
        is_admin=usuario.is_admin
    )

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    return db_usuario


@router.get("/", response_model=List[Usuario])
@limiter.limit("20/minute")
async def leer_usuarios(
        request: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(settings.DEFAULT_LIMIT, le=settings.MAX_LIMIT),
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_admin_user)
):
    """
    Obtiene la lista de usuarios (solo administradores).

    Este endpoint permite a los administradores ver todos los usuarios registrados.
    Soporta paginación con los parámetros skip y limit.
    """
    usuarios = db.query(UsuarioModel).order_by(UsuarioModel.id).offset(skip).limit(limit).all()
    return usuarios


@router.get("/me", response_model=Usuario)
async def leer_usuario_propio(
        current_user: Usuario = Depends(get_current_active_user)
):
    """
    Obtiene la información del usuario actual.

    Este endpoint permite a cualquier usuario autenticado ver su propia información.
    """
    return current_user


@router.get("/{usuario_id}", response_model=Usuario)
async def leer_usuario(
        usuario_id: int,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_admin_user)
):
    """
    Obtiene la información de un usuario específico (solo administradores).

    Este endpoint permite a los administradores ver la información de cualquier usuario.
    """
    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if db_usuario is None:
        raise NotFoundException("Usuario no encontrado")
    return db_usuario


@router.put("/me", response_model=Usuario)
async def actualizar_usuario_propio(
        usuario_update: UsuarioUpdate,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_active_user)
):
    """
    Actualiza la información del usuario actual.

    Este endpoint permite a cualquier usuario autenticado actualizar su propia información.
    No permite cambiar el estado de administrador.
    """
    # No permitir cambiar el estado de administrador
    if usuario_update.is_admin is not None:
        raise ForbiddenException("No puedes cambiar tu estado de administrador")

    # Verificar si se está actualizando el email y si ya existe
    if usuario_update.email and usuario_update.email != current_user.email:
        db_user = db.query(UsuarioModel).filter(UsuarioModel.email == usuario_update.email).first()
        if db_user:
            raise BadRequestException("El correo electrónico ya está registrado")

    # Actualizar usuario
    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.id == current_user.id).first()

    # Actualizar los campos proporcionados
    update_data = usuario_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        if key == "password" and value:
            setattr(db_usuario, "hashed_password", get_password_hash(value))
        elif value is not None:
            setattr(db_usuario, key, value)

    db.commit()
    db.refresh(db_usuario)

    return db_usuario


@router.put("/{usuario_id}", response_model=Usuario)
async def actualizar_usuario(
        usuario_id: int,
        usuario_update: UsuarioUpdate,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_admin_user)
):
    """
    Actualiza la información de un usuario específico (solo administradores).

    Este endpoint permite a los administradores actualizar la información de cualquier usuario.
    """
    # Verificar si el usuario existe
    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if db_usuario is None:
        raise NotFoundException("Usuario no encontrado")

    # Verificar si se está actualizando el email y si ya existe
    if usuario_update.email and usuario_update.email != db_usuario.email:
        db_user = db.query(UsuarioModel).filter(UsuarioModel.email == usuario_update.email).first()
        if db_user and db_user.id != usuario_id:
            raise BadRequestException("El correo electrónico ya está registrado")

    # Actualizar los campos proporcionados
    update_data = usuario_update.dict(exclude_unset=True)

    for key, value in update_data.items():
        if key == "password" and value:
            setattr(db_usuario, "hashed_password", get_password_hash(value))
        elif value is not None:
            setattr(db_usuario, key, value)

    db.commit()
    db.refresh(db_usuario)

    return db_usuario


@router.delete("/{usuario_id}", response_model=Usuario)
async def eliminar_usuario(
        usuario_id: int,
        db: Session = Depends(get_db),
        current_user: Usuario = Depends(get_current_admin_user)
):
    """
    Elimina un usuario (solo administradores).

    Este endpoint permite a los administradores eliminar cualquier usuario,
    excepto a sí mismos.
    """
    if usuario_id == current_user.id:
        raise BadRequestException("No puedes eliminar tu propio usuario")

    db_usuario = db.query(UsuarioModel).filter(UsuarioModel.id == usuario_id).first()
    if db_usuario is None:
        raise NotFoundException("Usuario no encontrado")

    db.delete(db_usuario)
    db.commit()

    return db_usuario