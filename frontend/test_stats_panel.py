#!/usr/bin/env python3
"""
Script para probar el panel de estadísticas del frontend.
"""

import sys
import os

# Añadir el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from components.stats_panel import test_stats_panel
    print("✅ Módulo de panel de estadísticas importado exitosamente")
    
    # Ejecutar la función de prueba
    test_stats_panel()
    
except ImportError as e:
    print(f"❌ Error al importar el módulo de panel de estadísticas: {e}")
    print("Asegúrate de que todas las dependencias están instaladas correctamente.")
except Exception as e:
    print(f"❌ Error al ejecutar el panel de estadísticas: {e}")