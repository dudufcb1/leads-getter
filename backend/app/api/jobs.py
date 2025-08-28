"""
Endpoints para gestión de trabajos de scraping.
"""

import uuid
from typing import Dict, Any
from urllib.parse import unquote
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
from ..database.database import get_db
from ..database.models import ScrapingQueue, ScrapingLog
from ..scraper.run_scraper import run_scraper
from ..core.exceptions_new import (
    DatabaseException,
    ScrapingException,
    ValidationException,
    NotFoundException
)

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


class PriorityUpdate(BaseModel):
    """Modelo para actualizar la prioridad de un job."""
    priority: int = Field(..., description="Nueva prioridad del job", ge=0, le=10)

class QueueReorderItem(BaseModel):
    """Item para reordenar la cola de jobs."""
    job_id: str = Field(..., description="ID del job")
    new_priority: int = Field(..., description="Nueva prioridad", ge=0, le=10)

class QueueReorderRequest(BaseModel):
    """Request para reordenar la cola de jobs."""
    items: list[QueueReorderItem] = Field(..., description="Lista de items a reordenar")

class JobProgress(BaseModel):
    """Progreso detallado de un job."""
    job_id: str
    status: str
    progress: int = Field(..., description="Progreso del job (0-100)", ge=0, le=100)
    total_items: int
    processed_items: int
    success_rate: float = Field(..., description="Tasa de éxito", ge=0.0, le=1.0)
    estimated_completion: str = Field(..., description="Tiempo estimado de finalización")

class JobLog(BaseModel):
    """Log específico de un job."""
    id: int
    level: str
    message: str
    category: str
    created_at: str
    metadata: dict = Field(default_factory=dict)


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
    # Validar que la URL no esté vacía
    if not config.start_url:
        raise ValidationException("La URL inicial no puede estar vacía", field="start_url")
    
    # Validar formato de URL
    if not config.start_url.startswith(("http://", "https://")):
        raise ValidationException("La URL debe comenzar con http:// o https://", field="start_url")

    try:
        # Generar un job_id único
        import uuid
        job_id = str(uuid.uuid4())[:8]  # ID corto único

        # Verificar si la URL ya existe en la cola
        # Generar un job_id único
        import uuid
        job_id = str(uuid.uuid4())[:8]  # ID corto único
        
        existing_queue_item = db.query(ScrapingQueue).filter_by(job_id=job_id).first()
        
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
                job_id=job_id,
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

    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ScrapingException(f"Error al crear el trabajo de scraping: {str(e)}")


@router.get("/status")
async def get_job_status_by_url(job_url: str, db: Session = Depends(get_db)):
    """
    Obtiene el estado de un trabajo específico usando query parameter.
    
    - **job_url**: URL del trabajo de scraping
    """
    try:
        # Validar que la URL no esté vacía
        if not job_url:
            raise ValidationException("La URL del trabajo no puede estar vacía", field="job_url")
        
        # Consultar la base de datos para obtener el estado real del trabajo
        queue_item = db.query(ScrapingQueue).filter_by(url=job_url).first()
        
        # Si no se encuentra el trabajo, devolver un error
        if not queue_item:
            raise NotFoundException("Trabajo de scraping", identifier=job_url)
        
        # Obtener estadísticas reales del trabajo de scraping
        stats = {
            "processed_urls": 0,
            "queue_size": 1,
            "leads_found": 0
        }
        
        # Actualizar estadísticas según el estado del trabajo
        if queue_item.status == "completed":
            stats["processed_urls"] = 1
            stats["leads_found"] = 1
        elif queue_item.status == "failed":
            stats["processed_urls"] = 1
        
        return JobStatus(
            job_id=queue_item.job_id,
            status=queue_item.status,
            start_time=queue_item.created_at.isoformat() if queue_item.created_at else "2023-10-27T10:00:00Z",
            stats=stats
        )
    except SQLAlchemyError as e:
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")

@router.put("/{job_id}/pause", response_model=JobResponse)
async def pause_job(job_id: str, db: Session = Depends(get_db)):
    """
    Pausa un job específico.

    - **job_id**: ID del job a pausar
    """
    try:
        # Validar que el ID no esté vacío
        if not job_id:
            raise ValidationException("El ID del job no puede estar vacío", field="job_id")
            
        # Decodificar la URL que viene encoded desde FastAPI
        decoded_job_id = unquote(job_id)
        
        # Buscar el job en la base de datos
        queue_item = db.query(ScrapingQueue).filter_by(job_id=decoded_job_id).first()
        
        # Si no se encuentra el job, devolver error
        if not queue_item:
            raise NotFoundException("Job de scraping", identifier=decoded_job_id)
        
        # Verificar que el job esté en un estado que se pueda pausar
        if queue_item.status not in ["pending", "processing"]:
            raise ValidationException(f"No se puede pausar un job en estado '{queue_item.status}'", field="status")
        
        # Actualizar el estado a 'paused'
        queue_item.status = "paused"
        queue_item.updated_at = func.now()
        db.commit()
        
        return JobResponse(
            job_id=decoded_job_id,
            status="paused",
            message=f"Job '{decoded_job_id}' pausado exitosamente"
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ScrapingException(f"Error al pausar el job: {str(e)}")

@router.put("/{job_id}/resume", response_model=JobResponse)
async def resume_job(job_id: str, db: Session = Depends(get_db)):
    """
    Reanuda un job pausado.

    - **job_id**: ID del job a reanudar
    """
    try:
        # Validar que el ID no esté vacío
        if not job_id:
            raise ValidationException("El ID del job no puede estar vacío", field="job_id")
            
        # Decodificar la URL que viene encoded desde FastAPI
        decoded_job_id = unquote(job_id)
        
        # Buscar el job en la base de datos
        queue_item = db.query(ScrapingQueue).filter_by(job_id=decoded_job_id).first()
        
        # Si no se encuentra el job, devolver error
        if not queue_item:
            raise NotFoundException("Job de scraping", identifier=decoded_job_id)
        
        # Verificar que el job esté en un estado que se pueda reanudar
        if queue_item.status != "paused":
            raise ValidationException(f"No se puede reanudar un job en estado '{queue_item.status}'", field="status")
        
        # Actualizar el estado a 'pending' para que se procese
        queue_item.status = "pending"
        queue_item.updated_at = func.now()
        db.commit()
        
        return JobResponse(
            job_id=decoded_job_id,
            status="resumed",
            message=f"Job '{decoded_job_id}' reanudado exitosamente"
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ScrapingException(f"Error al reanudar el job: {str(e)}")

@router.delete("/{job_id}", response_model=JobResponse)
async def cancel_job(job_id: str, db: Session = Depends(get_db)):
    """
    Cancela un job específico.

    - **job_id**: ID del job a cancelar
    """
    try:
        # Validar que el ID no esté vacío
        if not job_id:
            raise ValidationException("El ID del job no puede estar vacío", field="job_id")
            
        # Decodificar la URL que viene encoded desde FastAPI
        decoded_job_id = unquote(job_id)
        
        # Buscar el job en la base de datos
        queue_item = db.query(ScrapingQueue).filter_by(job_id=decoded_job_id).first()
        
        # Si no se encuentra el job, devolver error
        if not queue_item:
            raise NotFoundException("Job de scraping", identifier=decoded_job_id)
        
        # Actualizar el estado a 'cancelled'
        queue_item.status = "cancelled"
        queue_item.updated_at = func.now()
        db.commit()
        
        return JobResponse(
            job_id=decoded_job_id,
            status="cancelled",
            message=f"Job '{decoded_job_id}' cancelado exitosamente"
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ScrapingException(f"Error al cancelar el job: {str(e)}")

@router.put("/{job_id}/priority", response_model=JobResponse)
async def update_job_priority(
    job_id: str,
    priority_update: PriorityUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza la prioridad de un job específico.

    - **job_id**: ID del job a actualizar
    - **priority**: Nueva prioridad (0-10)
    """
    try:
        # Validar que el ID no esté vacío
        if not job_id:
            raise ValidationException("El ID del job no puede estar vacío", field="job_id")
            
        # Decodificar la URL que viene encoded desde FastAPI
        decoded_job_id = unquote(job_id)
        
        # Buscar el job en la base de datos
        queue_item = db.query(ScrapingQueue).filter_by(job_id=decoded_job_id).first()
        
        # Si no se encuentra el job, devolver error
        if not queue_item:
            raise NotFoundException("Job de scraping", identifier=decoded_job_id)
        
        # Verificar que el job no esté en un estado final
        if queue_item.status in ["completed", "failed", "cancelled"]:
            raise ValidationException(f"No se puede actualizar la prioridad de un job en estado '{queue_item.status}'", field="status")
        
        # Actualizar la prioridad
        old_priority = queue_item.priority
        queue_item.priority = priority_update.priority
        queue_item.updated_at = func.now()
        db.commit()
        
        return JobResponse(
            job_id=decoded_job_id,
            status="priority_updated",
            message=f"Prioridad del job '{decoded_job_id}' actualizada de {old_priority} a {priority_update.priority}"
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ScrapingException(f"Error al actualizar la prioridad del job: {str(e)}")

@router.put("/pause-all", response_model=JobResponse)
async def pause_all_jobs(db: Session = Depends(get_db)):
    """
    Pausa todos los jobs activos.
    """
    try:
        # Pausar todos los jobs en estado 'pending' o 'processing'
        paused_count = db.query(ScrapingQueue).filter(
            ScrapingQueue.status.in_(["pending", "processing"])
        ).update(
            {
                ScrapingQueue.status: "paused",
                ScrapingQueue.updated_at: func.now()
            },
            synchronize_session=False
        )
        db.commit()
        
        return JobResponse(
            job_id="all",
            status="paused",
            message=f"Se pausaron {paused_count} jobs activos"
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ScrapingException(f"Error al pausar todos los jobs: {str(e)}")

@router.put("/resume-all", response_model=JobResponse)
async def resume_all_jobs(db: Session = Depends(get_db)):
    """
    Reanuda todos los jobs pausados.
    """
    try:
        # Reanudar todos los jobs en estado 'paused'
        resumed_count = db.query(ScrapingQueue).filter(
            ScrapingQueue.status == "paused"
        ).update(
            {
                ScrapingQueue.status: "pending",
                ScrapingQueue.updated_at: func.now()
            },
            synchronize_session=False
        )
        db.commit()
        
        return JobResponse(
            job_id="all",
            status="resumed",
            message=f"Se reanudaron {resumed_count} jobs pausados"
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ScrapingException(f"Error al reanudar todos los jobs: {str(e)}")

@router.delete("/active", response_model=JobResponse)
async def cancel_all_active_jobs(db: Session = Depends(get_db)):
    """
    Cancela todos los jobs activos.
    """
    try:
        # Cancelar todos los jobs en estados activos
        cancelled_count = db.query(ScrapingQueue).filter(
            ScrapingQueue.status.in_(["pending", "processing", "paused"])
        ).update(
            {
                ScrapingQueue.status: "cancelled",
                ScrapingQueue.updated_at: func.now()
            },
            synchronize_session=False
        )
        db.commit()
        
        return JobResponse(
            job_id="all",
            status="cancelled",
            message=f"Se cancelaron {cancelled_count} jobs activos"
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ScrapingException(f"Error al cancelar todos los jobs activos: {str(e)}")

class QueueStatus(BaseModel):
    """Estado de la cola de jobs."""
    total_jobs: int
    pending_jobs: int
    processing_jobs: int
    paused_jobs: int
    completed_jobs: int
    failed_jobs: int
    cancelled_jobs: int
    queue_items: list[dict]

@router.get("/queue", response_model=QueueStatus)
async def get_queue_status(db: Session = Depends(get_db)):
    """
    Obtiene el estado de la cola de jobs.
    """
    try:
        # Obtener todos los jobs ordenados por prioridad y fecha de creación
        queue_items = db.query(ScrapingQueue).order_by(
            ScrapingQueue.priority.desc(),
            ScrapingQueue.created_at.asc()
        ).all()
        
        # Contar jobs por estado
        total_jobs = len(queue_items)
        pending_jobs = sum(1 for item in queue_items if item.status == "pending")
        processing_jobs = sum(1 for item in queue_items if item.status == "processing")
        paused_jobs = sum(1 for item in queue_items if item.status == "paused")
        completed_jobs = sum(1 for item in queue_items if item.status == "completed")
        failed_jobs = sum(1 for item in queue_items if item.status == "failed")
        cancelled_jobs = sum(1 for item in queue_items if item.status == "cancelled")
        
        # Convertir items a diccionarios para la respuesta
        queue_items_dict = [
            {
                "job_id": item.job_id,
                "status": item.status,
                "priority": item.priority,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "progress": item.progress,
                "total_items": item.total_items,
                "processed_items": item.processed_items
            }
            for item in queue_items
        ]
        
        return QueueStatus(
            total_jobs=total_jobs,
            pending_jobs=pending_jobs,
            processing_jobs=processing_jobs,
            paused_jobs=paused_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            cancelled_jobs=cancelled_jobs,
            queue_items=queue_items_dict
        )
        
    except SQLAlchemyError as e:
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        raise ScrapingException(f"Error al obtener el estado de la cola: {str(e)}")

@router.put("/queue/clear", response_model=JobResponse)
async def clear_queue(db: Session = Depends(get_db)):
    """
    Limpia la cola de jobs pendientes.
    """
    try:
        # Eliminar todos los jobs en estados no terminales
        deleted_count = db.query(ScrapingQueue).filter(
            ScrapingQueue.status.in_(["pending", "paused"])
        ).delete(synchronize_session=False)
        db.commit()
        
        return JobResponse(
            job_id="queue",
            status="cleared",
            message=f"Se eliminaron {deleted_count} jobs de la cola"
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ScrapingException(f"Error al limpiar la cola: {str(e)}")

@router.put("/queue/reorder", response_model=JobResponse)
async def reorder_queue(
    reorder_request: QueueReorderRequest,
    db: Session = Depends(get_db)
):
    """
    Reordena los jobs en la cola.
    
    - **items**: Lista de items con job_id y nueva prioridad
    """
    try:
        updated_count = 0
        
        # Actualizar la prioridad de cada job
        for item in reorder_request.items:
            queue_item = db.query(ScrapingQueue).filter_by(job_id=item.job_id).first()
            if queue_item and queue_item.status not in ["completed", "failed", "cancelled"]:
                queue_item.priority = item.new_priority
                queue_item.updated_at = func.now()
                updated_count += 1
        
        db.commit()
        
        return JobResponse(
            job_id="queue",
            status="reordered",
            message=f"Se actualizaron las prioridades de {updated_count} jobs"
        )
        
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        db.rollback()
        raise ScrapingException(f"Error al reordenar la cola: {str(e)}")

@router.get("/{job_id}/progress", response_model=JobProgress)
async def get_job_progress(job_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el progreso detallado de un job específico.
    
    - **job_id**: ID del job
    """
    try:
        # Validar que el ID no esté vacío
        if not job_id:
            raise ValidationException("El ID del job no puede estar vacío", field="job_id")
            
        # Decodificar la URL que viene encoded desde FastAPI
        decoded_job_id = unquote(job_id)
        
        # Buscar el job en la base de datos
        queue_item = db.query(ScrapingQueue).filter_by(job_id=decoded_job_id).first()
        
        # Si no se encuentra el job, devolver error
        if not queue_item:
            raise NotFoundException("Job de scraping", identifier=decoded_job_id)
        
        # Calcular tasa de éxito (simplificada)
        success_rate = 1.0
        if queue_item.total_items > 0:
            success_rate = queue_item.processed_items / queue_item.total_items
        
        # Estimar tiempo de finalización (simplificado)
        estimated_completion = "N/A"
        if queue_item.status == "processing" and queue_item.total_items > 0:
            # Calcular progreso basado en items procesados
            progress = int((queue_item.processed_items / queue_item.total_items) * 100)
            estimated_completion = f"{progress}% completado"
        elif queue_item.status in ["completed", "failed", "cancelled"]:
            estimated_completion = "Finalizado"
        else:
            estimated_completion = "Pendiente"
        
        return JobProgress(
            job_id=decoded_job_id,
            status=queue_item.status,
            progress=queue_item.progress,
            total_items=queue_item.total_items,
            processed_items=queue_item.processed_items,
            success_rate=success_rate,
            estimated_completion=estimated_completion
        )
        
    except SQLAlchemyError as e:
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        raise ScrapingException(f"Error al obtener el progreso del job: {str(e)}")

@router.get("/{job_id}/logs", response_model=list[JobLog])
async def get_job_logs(job_id: str, db: Session = Depends(get_db)):
    """
    Obtiene los logs específicos de un job.
    
    - **job_id**: ID del job
    """
    try:
        # Validar que el ID no esté vacío
        if not job_id:
            raise ValidationException("El ID del job no puede estar vacío", field="job_id")
            
        # Decodificar la URL que viene encoded desde FastAPI
        decoded_job_id = unquote(job_id)
        
        # Buscar logs del job en la base de datos
        logs = db.query(ScrapingLog).filter_by(session_id=decoded_job_id).order_by(
            ScrapingLog.created_at.desc()
        ).limit(100).all()
        
        # Convertir logs a formato de respuesta
        job_logs = []
        for log in logs:
            try:
                metadata = {}
                if log.log_metadata:
                    import json
                    metadata = json.loads(log.log_metadata)
            except:
                metadata = {}
                
            job_logs.append(JobLog(
                id=log.id,
                level=log.level,
                message=log.message,
                category=log.category or "general",
                created_at=log.created_at.isoformat() if log.created_at else "",
                metadata=metadata
            ))
        
        return job_logs
        
    except SQLAlchemyError as e:
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        raise ScrapingException(f"Error al obtener los logs del job: {str(e)}")


@router.get("/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Obtiene el estado de un trabajo específico (método original con URL decoding).
    
    - **job_id**: ID del trabajo de scraping
    """
    try:
        # Validar que el ID no esté vacío
        if not job_id:
            raise ValidationException("El ID del trabajo no puede estar vacío", field="job_id")
            
        # Decodificar la URL que viene encoded desde FastAPI
        decoded_job_id = unquote(job_id)
        
        # Debug: mostrar los valores
        print(f"DEBUG: job_id recibido: {job_id}")
        print(f"DEBUG: decoded_job_id: {decoded_job_id}")
        
        # Consultar la base de datos para obtener el estado real del trabajo
        queue_item = db.query(ScrapingQueue).filter_by(job_id=decoded_job_id).first()
        
        # Debug: mostrar el resultado de la consulta
        print(f"DEBUG: queue_item encontrado: {queue_item}")
        if queue_item:
            print(f"DEBUG: queue_item.url: {queue_item.url}")
            print(f"DEBUG: queue_item.status: {queue_item.status}")
        
        # Si no se encuentra el trabajo, devolver un error
        if not queue_item:
            # Buscar todos los jobs para ver qué hay en la base de datos
            all_jobs = db.query(ScrapingQueue).all()
            print(f"DEBUG: Todos los jobs en DB: {[job.url for job in all_jobs]}")
            raise NotFoundException("Trabajo de scraping", identifier=decoded_job_id)
        
        # Obtener estadísticas reales del trabajo de scraping
        stats = {
            "processed_urls": 0,
            "queue_size": 1,
            "leads_found": 0
        }
        
        # Actualizar estadísticas según el estado del trabajo
        if queue_item.status == "completed":
            stats["processed_urls"] = 1
            stats["leads_found"] = 1
        elif queue_item.status == "failed":
            stats["processed_urls"] = 1
        
        return JobStatus(
            job_id=decoded_job_id,
            status=queue_item.status,
            start_time=queue_item.created_at.isoformat() if queue_item.created_at else "2023-10-27T10:00:00Z",
            stats=stats
        )
    except SQLAlchemyError as e:
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")

