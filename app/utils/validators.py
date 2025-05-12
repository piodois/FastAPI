import re
from fastapi import HTTPException, status
from typing import Optional


def validate_email(email: str) -> bool:
    """Valida un correo electrónico."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password_strength(password: str) -> tuple[bool, Optional[str]]:
    """
    Valida la fortaleza de la contraseña.
    Devuelve (True, None) si la contraseña es fuerte o (False, mensaje_error) si no lo es.
    """
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"

    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una letra mayúscula"

    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una letra minúscula"

    if not re.search(r"\d", password):
        return False, "La contraseña debe contener al menos un número"

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "La contraseña debe contener al menos un carácter especial"

    return True, None


def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """
    Valida un nombre de usuario.
    Devuelve (True, None) si el nombre de usuario es válido o (False, mensaje_error) si no lo es.
    """
    if len(username) < 3:
        return False, "El nombre de usuario debe tener al menos 3 caracteres"

    if len(username) > 50:
        return False, "El nombre de usuario no puede tener más de 50 caracteres"

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "El nombre de usuario solo puede contener letras, números y guiones bajos"

    return True, None


def validate_required_field(field_name: str, value: Optional[str]) -> None:
    """Valida que un campo requerido no esté vacío."""
    if value is None or value.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El campo '{field_name}' es requerido"
        )