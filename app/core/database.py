from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
from .config import settings

# Crear el motor de base de datos
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True,  # Detecta conexiones desconectadas
    pool_recycle=3600,   # Recicla conexiones después de una hora
    echo=settings.DEBUG  # Mostrar consultas SQL en modo debug
)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Función para obtener la sesión de la BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Evento para establecer configuraciones específicas para SQL Server
@event.listens_for(Engine, "connect")
def set_mssql_options(dbapi_connection, connection_record):
    # Configurar opciones específicas de SQL Server si es necesario
    cursor = dbapi_connection.cursor()
    cursor.execute("SET NOCOUNT ON")  # Evita mensajes de recuento de filas
    cursor.close()