from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..exceptions import UnauthorizedException, ForbiddenException
from ..models import Usuario
from ..schemas import TokenData
from ..core.database import get_db
from ..core.config import settings

# Configuración de seguridad para contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Crea un hash de la contraseña."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT con los datos proporcionados."""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def decode_token(token: str) -> TokenData:
    """Decodifica un token JWT y devuelve los datos del token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        exp: datetime = datetime.fromtimestamp(payload.get("exp"))

        if username is None:
            raise UnauthorizedException("Token inválido")

        token_data = TokenData(username=username, exp=exp)
        return token_data
    except JWTError:
        raise UnauthorizedException("Token inválido o expirado")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> Usuario:
    """Obtiene el usuario actual basado en el token JWT."""
    try:
        token_data = decode_token(token)
        user = db.query(Usuario).filter(Usuario.username == token_data.username).first()

        if user is None:
            raise UnauthorizedException("Usuario no encontrado")

        return user
    except JWTError:
        raise UnauthorizedException("Token inválido o expirado")


async def get_current_active_user(
        current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """Verifica que el usuario actual esté activo."""
    if not current_user.is_active:
        raise ForbiddenException("Usuario inactivo")

    return current_user


async def get_current_admin_user(
        current_user: Usuario = Depends(get_current_active_user)
) -> Usuario:
    """Verifica que el usuario actual tenga permisos de administrador."""
    if not current_user.is_admin:
        raise ForbiddenException("Acceso denegado: se requieren privilegios de administrador")

    return current_user