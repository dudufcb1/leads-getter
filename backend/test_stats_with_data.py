#!/usr/bin/env python3
"""
Script para probar los endpoints de estadísticas con datos generados.
"""

import requests
import time
import json

# Configuración
BASE_URL = "http://devactivo.com/api/v1/stats"

def test_system_stats_with_data():
    """Prueba el endpoint de estadísticas del sistema con datos."""
    print("🔍 Probando endpoint de estadísticas del sistema con datos...")
    try:
        response = requests.get(f"{BASE_URL}/system")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Estadísticas del sistema obtenidas exitosamente")
            print(f"   Active jobs: {stats_data.get('active_jobs', 'N/A')}")
            print(f"   Total jobs today: {stats_data.get('total_jobs_today', 'N/A')}")
            print(f"   Total leads today: {stats_data.get('total_leads_today', 'N/A')}")
            print(f"   Total emails today: {stats_data.get('total_emails_today', 'N/A')}")
            
            # Mostrar información de salud del sistema
            health = stats_data.get('system_health', {})
            print(f"   CPU Usage: {health.get('cpu_usage_percent', 'N/A')}%")
            print(f"   Memory Usage: {health.get('memory_usage_mb', 'N/A')} MB")
            print(f"   Disk Usage: {health.get('disk_usage_gb', 'N/A')} GB")
            
            return True
        else:
            print(f"❌ Error al obtener estadísticas del sistema: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_scraping_stats_with_data():
    """Prueba el endpoint de estadísticas de scraping con datos."""
    print("🔍 Probando endpoint de estadísticas de scraping con datos...")
    try:
        response = requests.get(f"{BASE_URL}/scraping")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Estadísticas de scraping obtenidas exitosamente")
            print(f"   Period: {stats_data.get('period', 'N/A')}")
            print(f"   Total URLs processed: {stats_data.get('total_urls_processed', 'N/A')}")
            print(f"   Success rate: {stats_data.get('success_rate', 'N/A')}%")
            print(f"   Avg processing time: {stats_data.get('avg_processing_time', 'N/A')}ms")
            print(f"   Domains crawled: {stats_data.get('domains_crawled', 'N/A')}")
            print(f"   Duplicates filtered: {stats_data.get('duplicates_filtered', 'N/A')}")
            
            # Mostrar URLs por hora
            urls_by_hour = stats_data.get('urls_by_hour', [])
            if urls_by_hour:
                print(f"   URLs by hour (first 5):")
                for item in urls_by_hour[:5]:
                    print(f"     Hour {item.get('hour', 'N/A')}: {item.get('count', 'N/A')} URLs")
            
            # Mostrar dominios principales
            top_domains = stats_data.get('top_domains', [])
            if top_domains:
                print(f"   Top domains (first 5):")
                for domain in top_domains[:5]:
                    print(f"     {domain.get('domain', 'N/A')}: {domain.get('count', 'N/A')} websites")
            
            return True
        else:
            print(f"❌ Error al obtener estadísticas de scraping: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_historical_stats_with_data():
    """Prueba el endpoint de estadísticas históricas con datos."""
    print("🔍 Probando endpoint de estadísticas históricas con datos...")
    try:
        response = requests.get(f"{BASE_URL}/historical")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Estadísticas históricas obtenidas exitosamente")
            print(f"   Period: {stats_data.get('period', 'N/A')}")
            print(f"   Data points: {len(stats_data.get('data', []))}")
            
            # Mostrar algunos puntos de datos
            data_points = stats_data.get('data', [])
            if data_points:
                print(f"   Sample data points (first 3):")
                for point in data_points[:3]:
                    timestamp = point.get('timestamp', 'N/A')
                    websites = point.get('websites', 'N/A')
                    emails = point.get('emails', 'N/A')
                    jobs = point.get('jobs', 'N/A')
                    print(f"     {timestamp}: {websites} websites, {emails} emails, {jobs} jobs")
            
            return True
        else:
            print(f"❌ Error al obtener estadísticas históricas: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_performance_stats_with_data():
    """Prueba el endpoint de estadísticas de rendimiento con datos."""
    print("🔍 Probando endpoint de estadísticas de rendimiento con datos...")
    try:
        response = requests.get(f"{BASE_URL}/performance")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Estadísticas de rendimiento obtenidas exitosamente")
            print(f"   Timestamp: {stats_data.get('timestamp', 'N/A')}")
            
            # Mostrar rendimiento de scraping
            scraping_perf = stats_data.get('scraping_performance', {})
            if scraping_perf:
                print(f"   Scraping Performance:")
                print(f"     Requests per second: {scraping_perf.get('requests_per_second', 'N/A')}")
                print(f"     Avg response time: {scraping_perf.get('avg_response_time', 'N/A')}ms")
                print(f"     Error rate: {scraping_perf.get('error_rate_percent', 'N/A')}%")
            
            # Mostrar recursos del sistema
            system_resources = stats_data.get('system_resources', {})
            if system_resources:
                print(f"   System Resources:")
                print(f"     CPU Usage: {system_resources.get('cpu_percent', 'N/A')}%")
                print(f"     Memory Usage: {system_resources.get('memory_percent', 'N/A')}%")
            
            # Mostrar estado de la cola
            queue_status = stats_data.get('queue_status', {})
            if queue_status:
                print(f"   Queue Status:")
                print(f"     Pending URLs: {queue_status.get('pending_urls', 'N/A')}")
                print(f"     Processing URLs: {queue_status.get('processing_urls', 'N/A')}")
                print(f"     Completed URLs: {queue_status.get('completed_urls', 'N/A')}")
                print(f"     Failed URLs: {queue_status.get('failed_urls', 'N/A')}")
            
            return True
        else:
            print(f"❌ Error al obtener estadísticas de rendimiento: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_sources_stats_with_data():
    """Prueba el endpoint de estadísticas por fuente con datos."""
    print("🔍 Probando endpoint de estadísticas por fuente con datos...")
    try:
        response = requests.get(f"{BASE_URL}/sources")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Estadísticas por fuente obtenidas exitosamente")
            print(f"   Total sources: {len(stats_data.get('sources', []))}")
            print(f"   Top sources: {len(stats_data.get('top_sources', []))}")
            
            # Mostrar algunas fuentes
            sources = stats_data.get('sources', [])
            if sources:
                print(f"   Sample sources (first 3):")
                for source in sources[:3]:
                    domain = source.get('domain', 'N/A')
                    websites = source.get('websites_count', 'N/A')
                    emails = source.get('emails_count', 'N/A')
                    quality = source.get('avg_quality_score', 'N/A')
                    print(f"     {domain}: {websites} websites, {emails} emails, quality: {quality}")
            
            # Mostrar fuentes principales
            top_sources = stats_data.get('top_sources', [])
            if top_sources:
                print(f"   Top sources (first 3):")
                for source in top_sources[:3]:
                    domain = source.get('domain', 'N/A')
                    count = source.get('count', 'N/A')
                    print(f"     {domain}: {count} websites")
            
            return True
        else:
            print(f"❌ Error al obtener estadísticas por fuente: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    """Función principal de pruebas."""
    print("🚀 Iniciando pruebas de endpoints de estadísticas con datos...")
    print("=" * 70)
    
    tests = [
        ("Estadísticas del sistema", test_system_stats_with_data),
        ("Estadísticas de scraping", test_scraping_stats_with_data),
        ("Estadísticas históricas", test_historical_stats_with_data),
        ("Estadísticas de rendimiento", test_performance_stats_with_data),
        ("Estadísticas por fuente", test_sources_stats_with_data),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Ejecutando: {test_name}")
        print("-" * 50)
        success = test_func()
        results.append((test_name, success))
        
        if success:
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    # Resumen
    print("\n" + "=" * 70)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas con datos pasaron exitosamente!")
        return 0
    else:
        print("⚠️ Algunas pruebas fallaron")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)