from fastapi import HTTPException, status
from typing import Any, Dict, Optional

class BaseHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)

class UnauthorizedException(BaseHTTPException):
    def __init__(self, detail: str = "Credenciales inválidas") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )

class ForbiddenException(BaseHTTPException):
    def __init__(self, detail: str = "No tienes permisos suficientes") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )

class NotFoundException(BaseHTTPException):
    def __init__(self, detail: str = "Recurso no encontrado") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )

class BadRequestException(BaseHTTPException):
    def __init__(self, detail: str = "Solicitud inválida") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

class ConflictException(BaseHTTPException):
    def __init__(self, detail: str = "Conflicto con el recurso existente") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )

class InternalServerErrorException(BaseHTTPException):
    def __init__(self, detail: str = "Error interno del servidor") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )