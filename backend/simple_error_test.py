"""
Prueba simple para verificar el sistema de manejo de errores.
"""

import requests
import json

def test_error_handling():
    """Prueba el manejo de errores del sistema."""
    
    # URL base de la API
    base_url = "http://127.0.0.1:8000/api/v1"
    
    print("🧪 Probando sistema de manejo de errores...")
    
    # Prueba 1: Crear trabajo con URL vacía
    print("\n1. Probando creación de trabajo con URL vacía...")
    try:
        response = requests.post(f"{base_url}/jobs/", json={
            "start_url": "",
            "depth": 3,
            "languages": ["es", "en"],
            "delay": 2.0
        })
        
        print(f"   Código de estado: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"   ✅ Error de validación correctamente manejado: {data}")
        else:
            print(f"   ❌ Se esperaba código 400, se obtuvo {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error en la prueba: {e}")
    
    # Prueba 2: Crear trabajo con URL inválida
    print("\n2. Probando creación de trabajo con URL inválida...")
    try:
        response = requests.post(f"{base_url}/jobs/", json={
            "start_url": "invalid-url",
            "depth": 3,
            "languages": ["es", "en"],
            "delay": 2.0
        })
        
        print(f"   Código de estado: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"   ✅ Error de validación correctamente manejado: {data}")
        else:
            print(f"   ❌ Se esperaba código 400, se obtuvo {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error en la prueba: {e}")
    
    # Prueba 3: Obtener estado de trabajo inexistente
    print("\n3. Probando obtención de estado de trabajo inexistente...")
    try:
        response = requests.get(f"{base_url}/jobs/status?job_url=https://nonexistent.com")
        
        print(f"   Código de estado: {response.status_code}")
        if response.status_code == 404:
            data = response.json()
            print(f"   ✅ Error de recurso no encontrado correctamente manejado: {data}")
        else:
            print(f"   ❌ Se esperaba código 404, se obtuvo {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error en la prueba: {e}")
    
    # Prueba 4: Obtener leads con parámetros inválidos
    print("\n4. Probando obtención de leads con parámetros inválidos...")
    try:
        response = requests.get(f"{base_url}/leads?page=0&limit=150")
        
        print(f"   Código de estado: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"   ✅ Error de validación correctamente manejado: {data}")
        else:
            print(f"   ❌ Se esperaba código 400, se obtuvo {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error en la prueba: {e}")
    
    print("\n✅ Pruebas de manejo de errores completadas.")

if __name__ == "__main__":
    test_error_handling()