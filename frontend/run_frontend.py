"""
Punto de entrada principal para la aplicación frontend de generación de leads.
"""

import sys
import os

# Añadir el directorio raíz al path para poder importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from frontend.main import main

if __name__ == "__main__":
    main()