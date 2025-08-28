"""
Migración para agregar nuevos campos a la base de datos.
"""

import sys
import os

# Agregar el directorio raíz al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import sessionmaker
from backend.app.database.database import engine
from backend.app.database.models import Base

def upgrade():
    """Aplica la migración para agregar nuevos campos."""
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    # Si necesitamos agregar campos específicos a tablas existentes,
    # tendríamos que usar Alembic o una solución similar.
    # Por ahora, simplemente creamos las tablas si no existen.

def downgrade():
    """Revierte la migración."""
    # En una implementación real, aquí se revertirían los cambios
    # Por ahora, dejamos este método vacío
    pass

if __name__ == "__main__":
    upgrade()
    print("✅ Migración completada exitosamente")