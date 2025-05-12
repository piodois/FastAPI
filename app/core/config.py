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

        # Construir la URI de conexión a la base de datos
        if self.DB_TRUSTED_CONNECTION:
            self.SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc://{self.DB_HOST}/{self.DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
        else:
            self.SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server"


settings = Settings()