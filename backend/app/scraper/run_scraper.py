"""
Función para ejecutar el scraper desde la API.
"""

import subprocess
import sys
import os
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from ..database.models import ScrapingQueue


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
            "-a", f"job_id={job_id}",
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

        # Actualizar estado en la base de datos
        update_job_status = None
        if result.returncode == 0:
            print(f"✅ Scraping job {job_id} completed successfully")
            print("📋 STDOUT:")
            print(result.stdout)
            if result.stderr:
                print("📋 STDERR:")
                print(result.stderr)
            update_job_status = "completed"
        else:
            print(f"❌ Scraping job {job_id} failed")
            print("📋 STDOUT:")
            print(result.stdout)
            print("📋 STDERR:")
            print(result.stderr)
            update_job_status = "failed"
            
        # Actualizar estado en base de datos
        _update_job_status_in_db(job_id, update_job_status)

    except subprocess.TimeoutExpired:
        print(f"⏰ Scraping job {job_id} timed out")
        _update_job_status_in_db(job_id, "failed")
    except Exception as e:
        print(f"💥 Error running scraper for job {job_id}: {e}")
        _update_job_status_in_db(job_id, "failed")


def _update_job_status_in_db(job_id: str, status: str):
    """
    Actualiza el estado del job en la base de datos.
    
    Args:
        job_id: ID del job a actualizar
        status: Nuevo estado ('completed', 'failed', etc.)
    """
    try:
        # Crear conexión a la base de datos usando la configuración centralizada
        from ..core.config import settings
        engine = create_engine(settings.DATABASE_URL, echo=False)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Buscar el job en la base de datos
        queue_item = db.query(ScrapingQueue).filter_by(job_id=job_id).first()
        
        if queue_item:
            queue_item.status = status
            db.commit()
            print(f"🔄 Updated job status to '{status}' for job ID: {job_id}")
        else:
            print(f"⚠️ Job not found in database for job ID: {job_id}")
            
        db.close()
        
    except Exception as e:
        print(f"💥 Error updating job status in database: {e}")