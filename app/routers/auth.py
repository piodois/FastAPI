from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.database import get_db
from ..core.config import settings
from ..core.security import (
    verify_password,
    get_password_hash,
    create_access_token
)
from ..schemas.usuario import UsuarioCreate, Usuario
from ..schemas.token import Token
from ..models.usuario import Usuario as UsuarioModel
from ..exceptions import UnauthorizedException, BadRequestException
from ..utils.validators import validate_password_strength, validate_username

# Limiter para rate limiting
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["autenticación"]
)


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login_for_access_token(
        request: Request,
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: Session = Depends(get_db)
):
    """
    Inicia sesión y genera un token JWT.

    - **username**: Nombre de usuario
    - **password**: Contraseña

    Retorna un token JWT que debe ser utilizado en el encabezado de autorización
    para acceder a endpoints protegidos.
    """
    # Validar datos de entrada
    if not form_data.username or not form_data.password:
        raise BadRequestException("El nombre de usuario y la contraseña son obligatorios")

    # Buscar usuario
    user = db.query(UsuarioModel).filter(UsuarioModel.username == form_data.username).first()

    # Verificar usuario y contraseña
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise UnauthorizedException("Usuario o contraseña incorrectos")

    # Verificar si el usuario está activo
    if not user.is_active:
        raise UnauthorizedException("Usuario inactivo")

    # Generar token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    try:
        # Actualizar último login
        db_user = db.query(UsuarioModel).filter(UsuarioModel.id == user.id).first()
        if db_user:
            db_user.ultimo_login = datetime.utcnow()
            db.commit()
        else:
            # Si no se encuentra el usuario (esto no debería ocurrir normalmente)
            # pero simplemente continuamos sin actualizar último_login
            db.rollback()
            print(f"ADVERTENCIA: No se pudo actualizar último_login porque el usuario con ID {user.id} no existe.")
    except Exception as e:
        db.rollback()
        print(f"ERROR al actualizar último_login: {str(e)}")
        # Continuar a pesar del error en la actualización de último_login

    # Calcular tiempo de expiración para incluirlo en la respuesta
    expires_at = datetime.utcnow() + access_token_expires

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_at": expires_at
    }

@router.post("/registro", response_model=Usuario, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def registrar_usuario(
        request: Request,
        usuario: UsuarioCreate,
        db: Session = Depends(get_db)
):
    """
    Registra un nuevo usuario.

    - **email**: Correo electrónico del usuario (debe ser único)
    - **username**: Nombre de usuario (debe ser único)
    - **password**: Contraseña (debe cumplir requisitos de seguridad)
    - **nombre**: Nombre del usuario (opcional)
    - **apellido**: Apellido del usuario (opcional)

    Por defecto, los usuarios creados mediante este endpoint son usuarios normales,
    no administradores.
    """
    # Validar fortaleza de contraseña
    is_valid, mensaje = validate_password_strength(usuario.password)
    if not is_valid:
        raise BadRequestException(mensaje)

    # Validar formato de nombre de usuario
    is_valid, mensaje = validate_username(usuario.username)
    if not is_valid:
        raise BadRequestException(mensaje)

    # Para el registro de usuarios normales, no administradores
    usuario.is_admin = True

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