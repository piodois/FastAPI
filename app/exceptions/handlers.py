from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from jose import JWTError
from pydantic import ValidationError
import traceback
from typing import Union, Dict, Any


def setup_exception_handlers(app: FastAPI, debug: bool = False) -> None:
    """Configura los manejadores de excepciones para la aplicación."""

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Maneja excepciones de SQLAlchemy."""
        error_response = {
            "detail": "Error de base de datos",
            "type": "database_error"
        }

        if debug:
            error_response["error"] = str(exc)
            error_response["traceback"] = traceback.format_exc()

        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        # Manejar específicamente errores de integridad
        if isinstance(exc, IntegrityError):
            error_response["detail"] = "Violación de restricción de integridad"
            error_response["type"] = "integrity_error"
            status_code = status.HTTP_409_CONFLICT

            # Detectar errores específicos de integridad
            error_msg = str(exc).lower()
            if "unique" in error_msg or "duplicate" in error_msg:
                error_response["detail"] = "El registro ya existe"
            elif "foreign key" in error_msg:
                error_response["detail"] = "Referencia a un registro que no existe"

        return JSONResponse(
            status_code=status_code,
            content=error_response,
        )

    @app.exception_handler(JWTError)
    async def jwt_exception_handler(request: Request, exc: JWTError) -> JSONResponse:
        """Maneja excepciones relacionadas con tokens JWT."""
        error_response = {
            "detail": "Error de autenticación",
            "type": "authentication_error"
        }

        if debug:
            error_response["error"] = str(exc)

        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response,
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Maneja errores de validación de Pydantic."""
        errors = []
        for error in exc.errors():
            error_detail = {
                "loc": error["loc"],
                "msg": error["msg"],
                "type": error["type"]
            }
            errors.append(error_detail)

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Error de validación",
                "type": "validation_error",
                "errors": errors
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Maneja excepciones generales no capturadas por otros manejadores."""
        error_response = {
            "detail": "Error interno del servidor",
            "type": "server_error"
        }

        if debug:
            error_response["error"] = str(exc)
            error_response["traceback"] = traceback.format_exc()

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response,
        )