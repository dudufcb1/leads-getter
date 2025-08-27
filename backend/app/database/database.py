"""
Configuración de la base de datos y sesión de SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from ..core.config import settings

# Crear el engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Crear la clase base para los modelos
Base = declarative_base()

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependencia para obtener una sesión de base de datos.
    Se utiliza en las rutas de FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Crear todas las tablas en la base de datos.
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Eliminar todas las tablas de la base de datos.
    Útil para desarrollo y testing.
    """
    Base.metadata.drop_all(bind=engine)