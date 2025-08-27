"""
Función para ejecutar el scraper desde la API.
"""

import subprocess
import sys
import os
from pathlib import Path


def run_scraper(job_id: str, start_url: str, depth: int):
    """
    Ejecuta el scraper Scrapy para una URL específica.

    Args:
        job_id: ID del trabajo de scraping
        start_url: URL inicial para el scraping
        depth: Profundidad máxima de scraping
    """
    try:
        # Obtener la ruta del directorio del scraper
        scraper_dir = Path(__file__).parent

        # Obtener el directorio del backend para el PYTHONPATH
        backend_dir = Path(__file__).parent.parent.parent

        # Comando para ejecutar Scrapy
        cmd = [
            sys.executable, "-m", "scrapy", "crawl", "lead_spider",
            "-a", f"start_url={start_url}",
            "-a", f"depth={depth}",
            "-s", "LOG_LEVEL=INFO"
        ]

        # Configurar el entorno con PYTHONPATH
        env = {
            **dict(os.environ),
            'PYTHONPATH': str(backend_dir)
        }

        # Ejecutar el comando en el directorio del scraper
        result = subprocess.run(
            cmd,
            cwd=scraper_dir,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minutos timeout
            env=env
        )

        if result.returncode == 0:
            print(f"✅ Scraping job {job_id} completed successfully")
            print("📋 STDOUT:")
            print(result.stdout)
            if result.stderr:
                print("📋 STDERR:")
                print(result.stderr)
        else:
            print(f"❌ Scraping job {job_id} failed")
            print("📋 STDOUT:")
            print(result.stdout)
            print("📋 STDERR:")
            print(result.stderr)

    except subprocess.TimeoutExpired:
        print(f"⏰ Scraping job {job_id} timed out")
    except Exception as e:
        print(f"💥 Error running scraper for job {job_id}: {e}")