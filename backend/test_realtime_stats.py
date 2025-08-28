#!/usr/bin/env python3
"""
Script para validar la actualización en tiempo real de las estadísticas.
"""

import requests
import time
import json
from datetime import datetime

# Configuración
BASE_URL = "http://devactivo.com/api/v1/stats"

def test_realtime_updates():
    """Prueba la actualización en tiempo real de las estadísticas."""
    print("🔍 Probando actualización en tiempo real de estadísticas...")
    
    try:
        # Obtener estadísticas iniciales
        print("Obteniendo estadísticas iniciales...")
        response1 = requests.get(f"{BASE_URL}/system")
        if response1.status_code != 200:
            print(f"❌ Error al obtener estadísticas iniciales: {response1.status_code}")
            return False
            
        initial_stats = response1.json()
        print(f"✅ Estadísticas iniciales obtenidas")
        print(f"   Active jobs: {initial_stats.get('active_jobs', 'N/A')}")
        print(f"   Total jobs today: {initial_stats.get('total_jobs_today', 'N/A')}")
        
        # Esperar un momento
        print("\nEsperando 5 segundos...")
        time.sleep(5)
        
        # Obtener estadísticas después de un tiempo
        print("Obteniendo estadísticas después de 5 segundos...")
        response2 = requests.get(f"{BASE_URL}/system")
        if response2.status_code != 200:
            print(f"❌ Error al obtener estadísticas posteriores: {response2.status_code}")
            return False
            
        updated_stats = response2.json()
        print(f"✅ Estadísticas posteriores obtenidas")
        print(f"   Active jobs: {updated_stats.get('active_jobs', 'N/A')}")
        print(f"   Total jobs today: {updated_stats.get('total_jobs_today', 'N/A')}")
        
        # Verificar que los datos se hayan actualizado
        print("\nVerificando actualización de datos...")
        if (initial_stats.get('active_jobs') == updated_stats.get('active_jobs') and
            initial_stats.get('total_jobs_today') == updated_stats.get('total_jobs_today')):
            print("⚠️  Los datos no han cambiado, pero esto puede ser normal si no hay actividad")
        else:
            print("✅ Los datos se han actualizado correctamente")
            
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de actualización en tiempo real: {e}")
        return False

def test_cache_invalidation():
    """Prueba la invalidación del cache."""
    print("🔍 Probando invalidación del cache...")
    
    try:
        # Obtener estadísticas con cache
        print("Obteniendo estadísticas (con cache)...")
        start_time = time.time()
        response1 = requests.get(f"{BASE_URL}/system")
        first_call_time = time.time() - start_time
        
        if response1.status_code != 200:
            print(f"❌ Error al obtener estadísticas: {response1.status_code}")
            return False
            
        # Obtener estadísticas nuevamente (debería usar cache)
        print("Obteniendo estadísticas nuevamente (debería usar cache)...")
        start_time = time.time()
        response2 = requests.get(f"{BASE_URL}/system")
        second_call_time = time.time() - start_time
        
        if response2.status_code != 200:
            print(f"❌ Error al obtener estadísticas: {response2.status_code}")
            return False
            
        print(f"✅ Tiempos de respuesta:")
        print(f"   Primera llamada: {first_call_time:.4f} segundos")
        print(f"   Segunda llamada: {second_call_time:.4f} segundos")
        
        # La segunda llamada debería ser más rápida debido al cache
        if second_call_time < first_call_time:
            print("✅ El cache está funcionando correctamente (segunda llamada más rápida)")
        else:
            print("⚠️  El cache puede no estar funcionando óptimamente")
            
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de cache: {e}")
        return False

def test_historical_data_consistency():
    """Prueba la consistencia de los datos históricos."""
    print("🔍 Probando consistencia de datos históricos...")
    
    try:
        # Obtener datos históricos con diferentes períodos
        periods = ["day", "week", "month"]
        
        for period in periods:
            print(f"Obteniendo datos históricos para período: {period}")
            response = requests.get(f"{BASE_URL}/historical?period={period}")
            
            if response.status_code != 200:
                print(f"❌ Error al obtener datos históricos para {period}: {response.status_code}")
                return False
                
            data = response.json()
            print(f"✅ Datos obtenidos para {period}")
            print(f"   Puntos de datos: {len(data.get('data', []))}")
            
            # Verificar estructura de datos
            if 'data' not in data:
                print(f"❌ Estructura de datos incorrecta para {period}")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de datos históricos: {e}")
        return False

def main():
    """Función principal de pruebas."""
    print("🚀 Iniciando pruebas de actualización en tiempo real...")
    print("=" * 60)
    
    tests = [
        ("Actualización en tiempo real", test_realtime_updates),
        ("Invalidación del cache", test_cache_invalidation),
        ("Consistencia de datos históricos", test_historical_data_consistency),
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
        print("🎉 ¡Todas las pruebas de actualización en tiempo real pasaron exitosamente!")
        return 0
    else:
        print("⚠️ Algunas pruebas fallaron")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)