#!/usr/bin/env python3
"""
Script de prueba de integración para el scraper avanzado.
"""

import requests
import time
import json
import subprocess
import sys
import os
from pathlib import Path


def test_scraper_direct():
    """Prueba el scraper directamente con Scrapy."""
    print("🧪 Probando scraper directamente...")

    try:
        # Ejecutar scraper con una URL de prueba
        scraper_dir = Path(__file__).parent / "app" / "scraper"
        backend_dir = Path(__file__).parent

        cmd = [
            sys.executable, "-m", "scrapy", "crawl", "lead_spider",
            "-a", "start_url=https://httpbin.org/html",
            "-a", "depth=1",
            "-s", "LOG_LEVEL=INFO",
            "-s", "CLOSESPIDER_ITEMCOUNT=5"  # Limitar a 5 items para prueba rápida
        ]

        env = {
            **dict(os.environ),
            'PYTHONPATH': str(backend_dir)
        }

        result = subprocess.run(
            cmd,
            cwd=scraper_dir,
            capture_output=True,
            text=True,
            timeout=60,  # 1 minuto timeout
            env=env
        )

        if result.returncode == 0:
            print("✅ Scraper ejecutado exitosamente")
            print("📋 Output:")
            print(result.stdout[-500:])  # Últimos 500 caracteres
            return True
        else:
            print("❌ Error ejecutando scraper:")
            print(result.stderr[-500:])
            return False

    except Exception as e:
        print(f"💥 Error en test_scraper_direct: {e}")
        return False


def test_api_endpoints():
    """Prueba los endpoints de la API."""
    print("🧪 Probando endpoints de la API...")

    try:
        # Iniciar el servidor en background
        print("🚀 Iniciando servidor...")
        server_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=Path(__file__).parent,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Esperar a que el servidor inicie
        time.sleep(3)

        # Probar endpoint de creación de job
        api_url = "http://127.0.0.1:8000/api/v1/jobs/"
        job_data = {
            "start_url": "https://httpbin.org/html",
            "depth": 1,
            "languages": ["en"],
            "delay": 1.0
        }

        response = requests.post(api_url, json=job_data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            print(f"✅ API endpoint funciona: {result}")
            job_id = result.get('job_id')

            # Probar obtener estado del job
            status_url = f"http://127.0.0.1:8000/api/v1/jobs/{job_id}"
            status_response = requests.get(status_url, timeout=5)

            if status_response.status_code == 200:
                print("✅ Endpoint de estado funciona")
                return True
            else:
                print(f"❌ Error en endpoint de estado: {status_response.status_code}")
                return False
        else:
            print(f"❌ Error en API: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"💥 Error en test_api_endpoints: {e}")
        return False
    finally:
        # Detener el servidor
        if 'server_process' in locals():
            server_process.terminate()
            server_process.wait()


def test_database_models():
    """Prueba que los modelos de base de datos funcionan."""
    print("🧪 Probando modelos de base de datos...")

    try:
        from app.database.database import engine
        from app.database.models import Base, Website, Email, ScrapingSession, ScrapingLog

        # Crear todas las tablas
        Base.metadata.create_all(bind=engine)
        print("✅ Tablas creadas exitosamente")

        # Probar crear una sesión de scraping
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=engine)
        session = Session()

        # Crear una sesión de prueba
        test_session = ScrapingSession(
            session_id="test-session-123",
            start_url="https://example.com",
            status="completed",
            pages_processed=10,
            emails_found=5
        )

        session.add(test_session)
        session.commit()

        # Verificar que se guardó
        saved_session = session.query(ScrapingSession).filter_by(session_id="test-session-123").first()
        if saved_session:
            print("✅ Modelo ScrapingSession funciona")
            session.delete(saved_session)
            session.commit()
            return True
        else:
            print("❌ Error guardando sesión de prueba")
            return False

    except Exception as e:
        print(f"💥 Error en test_database_models: {e}")
        return False


def main():
    """Ejecuta todas las pruebas de integración."""
    print("🚀 Iniciando pruebas de integración del scraper avanzado...")
    print("=" * 60)

    tests = [
        ("Modelos de BD", test_database_models),
        ("Scraper directo", test_scraper_direct),
        ("API endpoints", test_api_endpoints),
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
    sys.exit(exit_code)