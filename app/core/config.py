from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import os

# Cargar variables de entorno
load_dotenv()


class Settings(BaseSettings):
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "API FastAPI SQL Server"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

    # Base de datos
    DB_HOST: str
    DB_PORT: str = "1433"  # Puerto por defecto para SQL Server
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: str
    DB_TRUSTED_CONNECTION: bool = False
    SQLALCHEMY_DATABASE_URI: Optional[str] = None

    # Seguridad
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Límites y paginación
    DEFAULT_LIMIT: int = 100
    MAX_LIMIT: int = 1000

    class Config:
        env_file = ".env"

    def __init__(self, **values: Any):
        super().__init__(**values)

        # Lista de posibles drivers ODBC para SQL Server
        odbc_drivers = [
            "ODBC Driver 18 for SQL Server",
            "ODBC Driver 17 for SQL Server",
            "SQL Server Native Client 11.0",
            "SQL Server",
            "FreeTDS"
        ]

        # Intentar detectar el driver disponible
        driver_encontrado = None
        try:
            import pyodbc
            available_drivers = pyodbc.drivers()

            # Buscar el primer driver disponible de nuestra lista preferida
            for driver in odbc_drivers:
                if driver in available_drivers:
                    driver_encontrado = driver
                    break

            # Si no encontramos ninguno en nuestra lista preferida, usar el primero disponible
            if not driver_encontrado and available_drivers:
                driver_encontrado = available_drivers[0]

            if driver_encontrado:
                print(f"INFO: Usando driver ODBC: '{driver_encontrado}'")
            else:
                # Si no hay drivers disponibles, usar uno común como fallback
                driver_encontrado = "ODBC Driver 17 for SQL Server"
                print(f"ADVERTENCIA: No se detectó un driver ODBC. Usando '{driver_encontrado}' por defecto")

        except ImportError:
            # Si pyodbc no está disponible por alguna razón
            driver_encontrado = "ODBC Driver 17 for SQL Server"
            print(f"ADVERTENCIA: No se pudo detectar drivers ODBC. Usando '{driver_encontrado}' por defecto")

        # Construir la URI de conexión a la base de datos con parámetros adicionales de seguridad
        driver_param = driver_encontrado.replace(' ', '+')

        if self.DB_TRUSTED_CONNECTION:
            self.SQLALCHEMY_DATABASE_URI = (
                f"mssql+pyodbc://{self.DB_HOST}/{self.DB_NAME}"
                f"?driver={driver_param}&trusted_connection=yes&TrustServerCertificate=yes"
            )
        else:
            # Asegurar que se escape correctamente la contraseña para URL
            import urllib.parse
            password_escaped = urllib.parse.quote_plus(self.DB_PASSWORD or "")

            self.SQLALCHEMY_DATABASE_URI = (
                f"mssql+pyodbc://{self.DB_USER}:{password_escaped}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
                f"?driver={driver_param}&TrustServerCertificate=yes"
            )


settings = Settings()