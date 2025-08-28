#!/usr/bin/env python3
"""
Script para probar los endpoints de estadísticas.
"""

import requests
import time
import json

# Configuración
BASE_URL = "http://devactivo.com/api/v1/stats"

def test_system_stats():
    """Prueba el endpoint de estadísticas del sistema."""
    print("🔍 Probando endpoint de estadísticas del sistema...")
    try:
        response = requests.get(f"{BASE_URL}/system")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Estadísticas del sistema obtenidas exitosamente")
            print(f"   Active jobs: {stats_data.get('active_jobs', 'N/A')}")
            print(f"   Total jobs today: {stats_data.get('total_jobs_today', 'N/A')}")
            print(f"   Total leads today: {stats_data.get('total_leads_today', 'N/A')}")
            print(f"   Total emails today: {stats_data.get('total_emails_today', 'N/A')}")
            return True
        else:
            print(f"❌ Error al obtener estadísticas del sistema: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_scraping_stats():
    """Prueba el endpoint de estadísticas de scraping."""
    print("🔍 Probando endpoint de estadísticas de scraping...")
    try:
        response = requests.get(f"{BASE_URL}/scraping")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Estadísticas de scraping obtenidas exitosamente")
            print(f"   Period: {stats_data.get('period', 'N/A')}")
            print(f"   Total URLs processed: {stats_data.get('total_urls_processed', 'N/A')}")
            print(f"   Success rate: {stats_data.get('success_rate', 'N/A')}%")
            return True
        else:
            print(f"❌ Error al obtener estadísticas de scraping: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_historical_stats():
    """Prueba el endpoint de estadísticas históricas."""
    print("🔍 Probando endpoint de estadísticas históricas...")
    try:
        response = requests.get(f"{BASE_URL}/historical")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Estadísticas históricas obtenidas exitosamente")
            print(f"   Period: {stats_data.get('period', 'N/A')}")
            print(f"   Data points: {len(stats_data.get('data', []))}")
            return True
        else:
            print(f"❌ Error al obtener estadísticas históricas: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_performance_stats():
    """Prueba el endpoint de estadísticas de rendimiento."""
    print("🔍 Probando endpoint de estadísticas de rendimiento...")
    try:
        response = requests.get(f"{BASE_URL}/performance")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Estadísticas de rendimiento obtenidas exitosamente")
            print(f"   Timestamp: {stats_data.get('timestamp', 'N/A')}")
            if 'scraping_performance' in stats_data:
                perf = stats_data['scraping_performance']
                print(f"   Avg response time: {perf.get('avg_response_time', 'N/A')}ms")
            return True
        else:
            print(f"❌ Error al obtener estadísticas de rendimiento: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_sources_stats():
    """Prueba el endpoint de estadísticas por fuente."""
    print("🔍 Probando endpoint de estadísticas por fuente...")
    try:
        response = requests.get(f"{BASE_URL}/sources")
        if response.status_code == 200:
            stats_data = response.json()
            print(f"✅ Estadísticas por fuente obtenidas exitosamente")
            print(f"   Sources: {len(stats_data.get('sources', []))}")
            print(f"   Top sources: {len(stats_data.get('top_sources', []))}")
            return True
        else:
            print(f"❌ Error al obtener estadísticas por fuente: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_cache_performance():
    """Prueba el rendimiento del sistema de caching."""
    print("🔍 Probando rendimiento del sistema de caching...")
    try:
        # Realizar primera llamada (sin cache)
        start_time = time.time()
        response1 = requests.get(f"{BASE_URL}/system")
        first_call_time = time.time() - start_time
        
        # Realizar segunda llamada (con cache)
        start_time = time.time()
        response2 = requests.get(f"{BASE_URL}/system")
        second_call_time = time.time() - start_time
        
        if response1.status_code == 200 and response2.status_code == 200:
            print(f"✅ Prueba de caching completada")
            print(f"   Primera llamada: {first_call_time:.4f} segundos")
            print(f"   Segunda llamada: {second_call_time:.4f} segundos")
            print(f"   Mejora: {((first_call_time - second_call_time) / first_call_time * 100):.2f}%")
            return True
        else:
            print(f"❌ Error en prueba de caching")
            return False
    except Exception as e:
        print(f"❌ Error en prueba de caching: {e}")
        return False

def main():
    """Función principal de pruebas."""
    print("🚀 Iniciando pruebas de endpoints de estadísticas...")
    print("=" * 60)
    
    tests = [
        ("Estadísticas del sistema", test_system_stats),
        ("Estadísticas de scraping", test_scraping_stats),
        ("Estadísticas históricas", test_historical_stats),
        ("Estadísticas de rendimiento", test_performance_stats),
        ("Estadísticas por fuente", test_sources_stats),
        ("Rendimiento del cache", test_cache_performance),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Ejecutando: {test_name}")
        print("-" * 40)
        success = test_func()
        results.append((test_name, success))
        
        if success:
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n📈 Resultado: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        return 0
    else:
        print("⚠️ Algunas pruebas fallaron")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)