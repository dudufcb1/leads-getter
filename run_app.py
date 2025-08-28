#!/usr/bin/env python3
"""
Script para ejecutar la aplicación completa del generador de leads.
"""

import subprocess
import sys
import os
import time
import signal
import atexit

# Variables para los procesos
backend_process = None
frontend_process = None

def cleanup():
    """Limpia los procesos al salir."""
    print("\n🛑 Cerrando aplicaciones...")
    if backend_process:
        try:
            backend_process.terminate()
            backend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            backend_process.kill()
        except Exception as e:
            print(f"Error al cerrar el backend: {e}")
    
    if frontend_process:
        try:
            frontend_process.terminate()
            frontend_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            frontend_process.kill()
        except Exception as e:
            print(f"Error al cerrar el frontend: {e}")
    
    print("✅ Aplicaciones cerradas correctamente")

def signal_handler(sig, frame):
    """Maneja las señales de cierre."""
    print("\n🛑 Señal de cierre recibida...")
    cleanup()
    sys.exit(0)

def main():
    """Función principal."""
    global backend_process, frontend_process
    
    # Registrar manejadores de señal
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    atexit.register(cleanup)
    
    print("🚀 Iniciando aplicación del generador de leads...")
    print("=" * 50)
    
    try:
        # Cambiar al directorio del backend
        backend_dir = os.path.join(os.path.dirname(__file__), "backend")
        
        # Iniciar el backend
        print("🔧 Iniciando backend...")
        # Usar el entorno virtual unificado
        venv_python = os.path.join(os.path.dirname(__file__), ".venv", "bin", "python")
        backend_process = subprocess.Popen([
            venv_python, "-m", "uvicorn", "app.main:app",
            "--host", "127.0.0.1", "--port", "8000", "--reload"
        ], cwd=backend_dir)
        
        # Esperar un momento para que el backend se inicie
        print("⏳ Esperando a que el backend se inicie...")
        time.sleep(5)
        
        # Verificar que el backend esté corriendo
        import requests
        try:
            response = requests.get("http://127.0.0.1:8000/api/v1/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend iniciado correctamente")
            else:
                print(f"❌ Error al iniciar el backend: {response.status_code}")
                return 1
        except Exception as e:
            print(f"❌ No se puede conectar con el backend: {e}")
            return 1
        
        # Iniciar el frontend
        print("🖥️  Iniciando frontend...")
        frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
        frontend_process = subprocess.Popen([
            sys.executable, "main.py"
        ], cwd=frontend_dir)
        
        print("✅ Frontend iniciado correctamente")
        print("\n🎯 Aplicación ejecutándose. Presiona Ctrl+C para detener.")
        print("   Backend: http://127.0.0.1:8000")
        print("   Frontend: Ventana de aplicación de escritorio")
        
        # Esperar a que los procesos terminen
        try:
            # Esperar a que termine el proceso del frontend (el principal)
            frontend_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Interrupción por teclado recibida...")
        except Exception as e:
            print(f"❌ Error en la ejecución: {e}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error al iniciar la aplicación: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)