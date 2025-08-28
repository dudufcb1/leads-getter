#!/usr/bin/env python3
"""
Script para iniciar el servidor backend del sistema de generación de leads.
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Verificar si el entorno virtual está activo
    import sys
    import os
    
    # Obtener la ruta del entorno virtual
    venv_path = os.path.join(os.path.dirname(__file__), "..", ".venv")
    
    # Verificar si el entorno virtual existe
    if os.path.exists(venv_path):
        # Verificar si el entorno virtual está activo
        if not hasattr(sys, 'real_prefix') and (not hasattr(sys, 'base_prefix') or sys.base_prefix == sys.prefix):
            print("⚠️  Advertencia: El entorno virtual no está activo")
            print("   Para activar el entorno virtual, ejecuta:")
            print("   source .venv/bin/activate")
    else:
        print("❌ Error: No se encuentra el entorno virtual en la ruta esperada")
        print("   Asegúrate de ejecutar este script desde el directorio correcto")
        sys.exit(1)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )