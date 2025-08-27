"""
Endpoints para gestión de trabajos de scraping.
"""

import uuid
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.models import ScrapingQueue
from ..scraper.run_scraper import run_scraper

router = APIRouter()


class JobConfig(BaseModel):
    """Configuración para un trabajo de scraping."""
    start_url: str = Field(..., description="URL inicial para el scraping")
    depth: int = Field(3, description="Profundidad máxima de scraping", ge=1, le=10)
    languages: list[str] = Field(["es", "en"], description="Idiomas a buscar")
    delay: float = Field(2.0, description="Delay entre requests", ge=0.1, le=10.0)


class JobResponse(BaseModel):
    """Respuesta para creación de trabajo."""
    job_id: str
    status: str
    message: str


class JobStatus(BaseModel):
    """Estado de un trabajo de scraping."""
    job_id: str
    status: str
    start_time: str
    stats: Dict[str, Any]


@router.post("/", response_model=JobResponse)
async def create_job(
    config: JobConfig,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Inicia un nuevo trabajo de scraping.

    - **start_url**: URL inicial para comenzar el scraping
    - **depth**: Profundidad máxima de scraping (1-10)
    - **languages**: Lista de idiomas a buscar
    - **delay**: Delay entre requests en segundos
    """
    try:
        # Generar ID único para el trabajo
        job_id = str(uuid.uuid4())

        # Verificar si la URL ya existe en la cola
        existing_queue_item = db.query(ScrapingQueue).filter_by(url=config.start_url).first()
        
        if existing_queue_item:
            # Si ya existe, actualizar el estado si es necesario
            if existing_queue_item.status in ["failed", "completed"]:
                existing_queue_item.status = "pending"
                existing_queue_item.attempts = 0
                db.commit()
                queue_item = existing_queue_item
            else:
                # Si ya está pending o processing, usar el existente
                queue_item = existing_queue_item
        else:
            # Crear nueva entrada en la cola de scraping
            queue_item = ScrapingQueue(
                url=config.start_url,
                priority=0,
                depth_level=0,
                status="pending",
                attempts=0
            )
            db.add(queue_item)
            db.commit()
            db.refresh(queue_item)

        # Iniciar el scraper en background
        background_tasks.add_task(run_scraper, job_id, config.start_url, config.depth)

        return JobResponse(
            job_id=job_id,
            status="starting",
            message="Scraping job started successfully."
        )

    except Exception as e:
        db.rollback()
        import traceback
        error_detail = f"Error creating job: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(f"🚨 ERROR IN CREATE_JOB: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el estado de un trabajo específico.

    - **job_id**: ID del trabajo de scraping
    """
    # Por ahora, devolver un estado básico
    # En una implementación completa, esto consultaría la base de datos
    # para obtener estadísticas reales del trabajo
    return JobStatus(
        job_id=job_id,
        status="running",
        start_time="2023-10-27T10:00:00Z",
        stats={
            "processed_urls": 0,
            "queue_size": 1,
            "leads_found": 0
        }
    )


@router.delete("/{job_id}", response_model=JobResponse)
async def stop_job(job_id: str):
    """
    Detiene (cancela) un trabajo en ejecución.

    - **job_id**: ID del trabajo a detener
    """
    # Por ahora, devolver una respuesta básica
    # En una implementación completa, esto debería:
    # 1. Verificar que el trabajo existe
    # 2. Detener el proceso de scraping si está corriendo
    # 3. Actualizar el estado en la base de datos
    return JobResponse(
        job_id=job_id,
        status="stopping",
        message="Scraping job is being stopped."
    )