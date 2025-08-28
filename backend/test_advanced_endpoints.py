#!/usr/bin/env python3
"""
Script para probar los endpoints de control avanzado de jobs.
"""

import requests
import time
import json

# Configuración
BASE_URL = "http://127.0.0.1:8000/api/v1/jobs"
TEST_URL = "https://example.com"

def test_create_job():
    """Prueba crear un job de scraping."""
    print("🔍 Probando creación de job...")
    payload = {
        "start_url": TEST_URL,
        "depth": 2,
        "languages": ["es", "en"],
        "delay": 1.0
    }
    
    try:
        response = requests.post(f"{BASE_URL}/", json=payload)
        if response.status_code == 200:
            job_data = response.json()
            print(f"✅ Job creado exitosamente: {job_data['job_id']}")
            return job_data['job_id']
        else:
            print(f"❌ Error al crear job: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_get_job_status(job_id):
    """Prueba obtener el estado de un job."""
    print(f"🔍 Probando obtención de estado para job {job_id}...")
    try:
        response = requests.get(f"{BASE_URL}/{job_id}")
        if response.status_code == 200:
            status_data = response.json()
            print(f"✅ Estado obtenido: {status_data['status']}")
            return status_data
        else:
            print(f"❌ Error al obtener estado: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_pause_job(job_id):
    """Prueba pausar un job."""
    print(f"🔍 Probando pausa de job {job_id}...")
    try:
        response = requests.put(f"{BASE_URL}/{job_id}/pause")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job pausado: {result['message']}")
            return True
        else:
            print(f"❌ Error al pausar job: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_resume_job(job_id):
    """Prueba reanudar un job."""
    print(f"🔍 Probando reanudación de job {job_id}...")
    try:
        response = requests.put(f"{BASE_URL}/{job_id}/resume")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job reanudado: {result['message']}")
            return True
        else:
            print(f"❌ Error al reanudar job: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_update_job_priority(job_id):
    """Prueba actualizar la prioridad de un job."""
    print(f"🔍 Probando actualización de prioridad para job {job_id}...")
    payload = {"priority": 5}
    try:
        response = requests.put(f"{BASE_URL}/{job_id}/priority", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Prioridad actualizada: {result['message']}")
            return True
        else:
            print(f"❌ Error al actualizar prioridad: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_get_queue_status():
    """Prueba obtener el estado de la cola."""
    print("🔍 Probando obtención de estado de cola...")
    try:
        response = requests.get(f"{BASE_URL}/queue")
        if response.status_code == 200:
            queue_data = response.json()
            print(f"✅ Estado de cola obtenido: {queue_data['total_jobs']} jobs totales")
            return queue_data
        else:
            print(f"❌ Error al obtener estado de cola: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_pause_all_jobs():
    """Prueba pausar todos los jobs."""
    print("🔍 Probando pausa de todos los jobs...")
    try:
        response = requests.put(f"{BASE_URL}/pause-all")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Todos los jobs pausados: {result['message']}")
            return True
        else:
            print(f"❌ Error al pausar todos los jobs: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_resume_all_jobs():
    """Prueba reanudar todos los jobs."""
    print("🔍 Probando reanudación de todos los jobs...")
    try:
        response = requests.put(f"{BASE_URL}/resume-all")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Todos los jobs reanudados: {result['message']}")
            return True
        else:
            print(f"❌ Error al reanudar todos los jobs: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_clear_queue():
    """Prueba limpiar la cola."""
    print("🔍 Probando limpieza de cola...")
    try:
        response = requests.put(f"{BASE_URL}/queue/clear")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Cola limpiada: {result['message']}")
            return True
        else:
            print(f"❌ Error al limpiar cola: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_get_job_progress(job_id):
    """Prueba obtener el progreso de un job."""
    print(f"🔍 Probando obtención de progreso para job {job_id}...")
    try:
        response = requests.get(f"{BASE_URL}/{job_id}/progress")
        if response.status_code == 200:
            progress_data = response.json()
            print(f"✅ Progreso obtenido: {progress_data['progress']}%")
            return progress_data
        else:
            print(f"❌ Error al obtener progreso: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def test_get_job_logs(job_id):
    """Prueba obtener los logs de un job."""
    print(f"🔍 Probando obtención de logs para job {job_id}...")
    try:
        response = requests.get(f"{BASE_URL}/{job_id}/logs")
        if response.status_code == 200:
            logs_data = response.json()
            print(f"✅ Logs obtenidos: {len(logs_data)} entradas")
            return logs_data
        else:
            print(f"❌ Error al obtener logs: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def main():
    """Función principal de pruebas."""
    print("🚀 Iniciando pruebas de endpoints avanzados...")
    print("=" * 50)
    
    # Crear un job para las pruebas
    job_id = test_create_job()
    if not job_id:
        print("❌ No se pudo crear el job, terminando pruebas.")
        return
    
    time.sleep(2)  # Esperar un momento para que el job se procese
    
    # Probar endpoints individuales
    test_get_job_status(job_id)
    test_update_job_priority(job_id)
    test_get_job_progress(job_id)
    test_get_job_logs(job_id)
    
    # Probar control de jobs individuales
    test_pause_job(job_id)
    time.sleep(1)
    test_resume_job(job_id)
    
    # Probar endpoints de cola
    test_get_queue_status()
    
    # Probar control masivo (comentado para no afectar otros jobs)
    # test_pause_all_jobs()
    # time.sleep(1)
    # test_resume_all_jobs()
    
    print("=" * 50)
    print("✅ Pruebas completadas!")

if __name__ == "__main__":
    main()