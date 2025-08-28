"""
Script de demostración para los endpoints de estadísticas usando devactivo.com como ejemplo.
"""

import requests
import time
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8000"
API_PREFIX = "/api/v1"

def demo_stats_endpoints():
    """Demostración de los endpoints de estadísticas usando devactivo.com como ejemplo."""
    
    print("🚀 Demostración de Endpoints de Estadísticas")
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
    time.sleep(3)
    
    # 2. Obtener estadísticas del sistema
    print("\n2. Obteniendo estadísticas del sistema...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/stats/system")
        
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Estadísticas del sistema obtenidas:")
            print(f"   Jobs activos: {stats_data['active_jobs']}")
            print(f"   Jobs hoy: {stats_data['total_jobs_today']}")
            print(f"   Leads hoy: {stats_data['total_leads_today']}")
            print(f"   Emails hoy: {stats_data['total_emails_today']}")
            print(f"   Salud del sistema: CPU {stats_data['system_health']['cpu_usage_percent']}%")
        else:
            print(f"❌ Error al obtener estadísticas del sistema: {response.status_code}")
            print(f"   Detalle: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 3. Obtener estadísticas de scraping
    print("\n3. Obteniendo estadísticas de scraping...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/stats/scraping?period=day")
        
        if response.status_code == 200:
            scraping_data = response.json()
            print(f"✅ Estadísticas de scraping obtenidas:")
            print(f"   Período: {scraping_data['period']}")
            print(f"   URLs procesadas: {scraping_data['total_urls_processed']}")
            print(f"   Tasa de éxito: {scraping_data['success_rate']}%")
            print(f"   Tiempo promedio: {scraping_data['avg_processing_time']}ms")
            print(f"   Dominios crawleados: {scraping_data['domains_crawled']}")
        else:
            print(f"❌ Error al obtener estadísticas de scraping: {response.status_code}")
            print(f"   Detalle: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 4. Obtener estadísticas avanzadas
    print("\n4. Obteniendo estadísticas avanzadas...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/advanced-stats/advanced?days=30")
        
        if response.status_code == 200:
            advanced_data = response.json()
            print(f"✅ Estadísticas avanzadas obtenidas:")
            print(f"   Total websites: {advanced_data['websites']['total_websites']}")
            print(f"   Websites con emails: {advanced_data['websites']['websites_with_emails']}")
            print(f"   Total emails: {advanced_data['emails']['total_emails']}")
            print(f"   Emails únicos: {advanced_data['emails']['unique_emails']}")
            print(f"   Total jobs: {advanced_data['jobs']['total_jobs']}")
        else:
            print(f"❌ Error al obtener estadísticas avanzadas: {response.status_code}")
            print(f"   Detalle: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 5. Obtener estadísticas en tiempo real
    print("\n5. Obteniendo estadísticas en tiempo real...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/advanced-stats/realtime")
        
        if response.status_code == 200:
            realtime_data = response.json()
            print(f"✅ Estadísticas en tiempo real obtenidas:")
            print(f"   Sesiones activas: {realtime_data['active_sessions']}")
            print(f"   Jobs procesando: {realtime_data['processing_jobs']}")
            print(f"   Emails última hora: {realtime_data['emails_found_last_hour']}")
            print(f"   Websites última hora: {realtime_data['websites_processed_last_hour']}")
            print(f"   Carga del sistema: {realtime_data['system_load']}")
        else:
            print(f"❌ Error al obtener estadísticas en tiempo real: {response.status_code}")
            print(f"   Detalle: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 6. Obtener estadísticas de un dominio específico
    print("\n6. Obteniendo estadísticas del dominio devactivo.com...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/advanced-stats/domain/devactivo.com")
        
        if response.status_code == 200:
            domain_data = response.json()
            print(f"✅ Estadísticas del dominio obtenidas:")
            print(f"   Dominio: {domain_data['domain']}")
            print(f"   Total websites: {domain_data['total_websites']}")
            print(f"   Websites con emails: {domain_data['websites_with_emails']}")
            print(f"   Total emails: {domain_data['total_emails']}")
            print(f"   Emails únicos: {domain_data['unique_emails']}")
            print(f"   Puntuación de calidad: {domain_data['average_quality_score']}")
        else:
            print(f"❌ Error al obtener estadísticas del dominio: {response.status_code}")
            print(f"   Detalle: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    # 7. Obtener estadísticas detalladas de un job
    print("\n7. Obteniendo estadísticas detalladas del job...")
    try:
        response = requests.get(f"{BASE_URL}{API_PREFIX}/advanced-stats/job/{job_id}/detailed")
        
        if response.status_code == 200:
            job_stats_data = response.json()
            print(f"✅ Estadísticas detalladas del job obtenidas:")
            print(f"   Job ID: {job_stats_data['job_id']}")
            print(f"   Estado: {job_stats_data['status']}")
            print(f"   Progreso: {job_stats_data['progress']}%")
            print(f"   Items procesados: {job_stats_data['processed_items']}/{job_stats_data['total_items']}")
            print(f"   Intentos: {job_stats_data['attempts']}")
        else:
            print(f"❌ Error al obtener estadísticas detalladas del job: {response.status_code}")
            print(f"   Detalle: {response.text}")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Demostración completada")

if __name__ == "__main__":
    demo_stats_endpoints()