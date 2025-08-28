"""
Script de demostración para los endpoints de control avanzado usando devactivo.com
"""

import requests
import time
import json

# Configuración
BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = "/api/v1"

def demo_control_endpoints():
    """Demostración de los endpoints de control avanzado."""
    
    print("🚀 Demostración de Endpoints de Control Avanzado")
    print("=" * 50)
    
    # 1. Crear un job de scraping para devactivo.com
    print("\n1. Creando job de scraping para devactivo.com...")
    try:
        response = requests.post(
            f"{BASE_URL}{API_PREFIX}/jobs",
            json={
                "start_url": "https://devactivo.com",
                "depth": 2,
                "languages": ["es", "en"],
                "delay": 1.0
            }
        )
        
        if response.status_code == 200:
            job_data = response.json()
            job_id = job_data["job_id"]
            print(f"✅ Job creado exitosamente: {job_id}")
            print(f"   Estado: {job_data['status']}")
            print(f"   Mensaje: {job_data['message']}")
        else:
            print(f"❌ Error al crear job: {response.status_code}")
            print(f"   Detalle: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return
    
    # Esperar un momento para que el job se procese
    print("\n   Esperando a que el job se inicialice...")
    time.sleep(2)
    
    # 2. Obtener el estado del job
    print("\n2. Obteniendo estado del job...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/jobs/{job_id}")
        
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Estado obtenido:")
            print(f"   Job ID: {status_data['job_id']}")
            print(f"   Estado: {status_data['status']}")
            print(f"   Estadísticas: {status_data['stats']}")
        else:
            print(f"❌ Error al obtener estado: {response.status_code}")
            print(f"   Detalle: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 3. Pausar el job (si está en estado válido)
    print("\n3. Pausando el job...")
    try:
        response = requests.post(f"{BASE_URL}{API_PREFIX}/control/{job_id}/pause")
        
        if response.status_code == 200:
            pause_data = response.json()
            print(f"✅ Job pausado:")
            print(f"   Job ID: {pause_data['job_id']}")
            print(f"   Estado: {pause_data['status']}")
            print(f"   Mensaje: {pause_data['message']}")
        else:
            print(f"ℹ️  No se pudo pausar el job: {response.status_code}")
            print(f"   Detalle: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 4. Reanudar el job
    print("\n4. Reanudando el job...")
    try:
        response = requests.post(f"{BASE_URL}{API_PREFIX}/control/{job_id}/resume")
        
        if response.status_code == 200:
            resume_data = response.json()
            print(f"✅ Job reanudado:")
            print(f"   Job ID: {resume_data['job_id']}")
            print(f"   Estado: {resume_data['status']}")
            print(f"   Mensaje: {resume_data['message']}")
        else:
            print(f"ℹ️  No se pudo reanudar el job: {response.status_code}")
            print(f"   Detalle: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 5. Obtener progreso del job
    print("\n5. Obteniendo progreso del job...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/jobs/{job_id}/progress")
        
        if response.status_code == 200:
            progress_data = response.json()
            print(f"✅ Progreso obtenido:")
            print(f"   Job ID: {progress_data['job_id']}")
            print(f"   Estado: {progress_data['status']}")
            print(f"   Progreso: {progress_data['progress']}%")
            print(f"   Items procesados: {progress_data['processed_items']}/{progress_data['total_items']}")
            print(f"   Tasa de éxito: {progress_data['success_rate']:.2%}")
        else:
            print(f"❌ Error al obtener progreso: {response.status_code}")
            print(f"   Detalle: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 6. Obtener logs del job
    print("\n6. Obteniendo logs del job...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/jobs/{job_id}/logs")
        
        if response.status_code == 200:
            logs_data = response.json()
            print(f"✅ Logs obtenidos:")
            print(f"   Número de logs: {len(logs_data)}")
            if logs_data:
                print(f"   Último log: {logs_data[0]['message']}")
        else:
            print(f"❌ Error al obtener logs: {response.status_code}")
            print(f"   Detalle: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 7. Detener el job
    print("\n7. Deteniendo el job...")
    try:
        response = requests.post(f"{BASE_URL}{API_PREFIX}/control/{job_id}/stop")
        
        if response.status_code == 200:
            stop_data = response.json()
            print(f"✅ Job detenido:")
            print(f"   Job ID: {stop_data['job_id']}")
            print(f"   Estado: {stop_data['status']}")
            print(f"   Mensaje: {stop_data['message']}")
        else:
            print(f"ℹ️  No se pudo detener el job: {response.status_code}")
            print(f"   Detalle: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Demostración completada")

if __name__ == "__main__":
    demo_control_endpoints()