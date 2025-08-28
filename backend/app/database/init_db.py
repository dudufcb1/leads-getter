"""
Script para inicializar la base de datos.
"""

import sys
import os

# Agregar el directorio raíz al path para importaciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.database import create_tables

if __name__ == "__main__":
    create_tables()
    print("✅ Base de datos inicializada exitosamente")