"""
Endpoints para control avanzado de trabajos de scraping.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.models import ScrapingQueue
from ..core.exceptions_new import NotFoundException, ValidationException
from pydantic import BaseModel
from typing import List
import uuid

router = APIRouter()

class JobActionResponse(BaseModel):
    """Respuesta para acciones de control de jobs."""
    job_id: str
    status: str
    message: str

class BulkJobActionRequest(BaseModel):
    """Request para acciones masivas en jobs."""
    job_ids: List[str]

class BulkJobActionResponse(BaseModel):
    """Respuesta para acciones masivas en jobs."""
    success_count: int
    failed_count: int
    details: List[JobActionResponse]

@router.post("/{job_id}/stop", response_model=JobActionResponse)
async def stop_job(job_id: str, db: Session = Depends(get_db)):
    """
    Detiene un job específico.
    
    - **job_id**: ID del job a detener
    """
    try:
        # Validar que el ID no esté vacío
        if not job_id:
            raise ValidationException("El ID del job no puede estar vacío", field="job_id")
            
        # Buscar el job en la base de datos
        queue_item = db.query(ScrapingQueue).filter_by(job_id=job_id).first()
        
        # Si no se encuentra el job, devolver error
        if not queue_item:
            raise NotFoundException("Job de scraping", identifier=job_id)
        
        # Verificar que el job esté en un estado que se pueda detener
        if queue_item.status not in ["pending", "processing", "paused"]:
            raise ValidationException(f"No se puede detener un job en estado '{queue_item.status}'", field="status")
        
        # Actualizar el estado a 'cancelled'
        queue_item.status = "cancelled"
        db.commit()
        
        return JobActionResponse(
            job_id=job_id,
            status="stopped",
            message=f"Job '{job_id}' detenido exitosamente"
        )
        
    except Exception as e:
        db.rollback()
        raise e

@router.post("/{job_id}/pause", response_model=JobActionResponse)
async def pause_job(job_id: str, db: Session = Depends(get_db)):
    """
    Pausa un job específico.
    
    - **job_id**: ID del job a pausar
    """
    try:
        # Validar que el ID no esté vacío
        if not job_id:
            raise ValidationException("El ID del job no puede estar vacío", field="job_id")
            
        # Buscar el job en la base de datos
        queue_item = db.query(ScrapingQueue).filter_by(job_id=job_id).first()
        
        # Si no se encuentra el job, devolver error
        if not queue_item:
            raise NotFoundException("Job de scraping", identifier=job_id)
        
        # Verificar que el job esté en un estado que se pueda pausar
        if queue_item.status not in ["pending", "processing"]:
            raise ValidationException(f"No se puede pausar un job en estado '{queue_item.status}'", field="status")
        
        # Actualizar el estado a 'paused'
        queue_item.status = "paused"
        db.commit()
        
        return JobActionResponse(
            job_id=job_id,
            status="paused",
            message=f"Job '{job_id}' pausado exitosamente"
        )
        
    except Exception as e:
        db.rollback()
        raise e

@router.post("/{job_id}/resume", response_model=JobActionResponse)
async def resume_job(job_id: str, db: Session = Depends(get_db)):
    """
    Reanuda un job pausado.
    
    - **job_id**: ID del job a reanudar
    """
    try:
        # Validar que el ID no esté vacío
        if not job_id:
            raise ValidationException("El ID del job no puede estar vacío", field="job_id")
            
        # Buscar el job en la base de datos
        queue_item = db.query(ScrapingQueue).filter_by(job_id=job_id).first()
        
        # Si no se encuentra el job, devolver error
        if not queue_item:
            raise NotFoundException("Job de scraping", identifier=job_id)
        
        # Verificar que el job esté en un estado que se pueda reanudar
        if queue_item.status != "paused":
            raise ValidationException(f"No se puede reanudar un job en estado '{queue_item.status}'", field="status")
        
        # Actualizar el estado a 'pending' para que se procese
        queue_item.status = "pending"
        db.commit()
        
        return JobActionResponse(
            job_id=job_id,
            status="resumed",
            message=f"Job '{job_id}' reanudado exitosamente"
        )
        
    except Exception as e:
        db.rollback()
        raise e

@router.post("/stop-all", response_model=BulkJobActionResponse)
async def stop_all_jobs(db: Session = Depends(get_db)):
    """
    Detiene todos los jobs activos.
    """
    try:
        # Detener todos los jobs en estados activos
        stopped_count = db.query(ScrapingQueue).filter(
            ScrapingQueue.status.in_(["pending", "processing", "paused"])
        ).update(
            {
                ScrapingQueue.status: "cancelled"
            },
            synchronize_session=False
        )
        db.commit()
        
        return BulkJobActionResponse(
            success_count=stopped_count,
            failed_count=0,
            details=[JobActionResponse(
                job_id="all",
                status="stopped",
                message=f"Se detuvieron {stopped_count} jobs activos"
            )]
        )
        
    except Exception as e:
        db.rollback()
        raise e

@router.post("/pause-all", response_model=BulkJobActionResponse)
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
                ScrapingQueue.status: "paused"
            },
            synchronize_session=False
        )
        db.commit()
        
        return BulkJobActionResponse(
            success_count=paused_count,
            failed_count=0,
            details=[JobActionResponse(
                job_id="all",
                status="paused",
                message=f"Se pausaron {paused_count} jobs activos"
            )]
        )
        
    except Exception as e:
        db.rollback()
        raise e

@router.post("/resume-all", response_model=BulkJobActionResponse)
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
                ScrapingQueue.status: "pending"
            },
            synchronize_session=False
        )
        db.commit()
        
        return BulkJobActionResponse(
            success_count=resumed_count,
            failed_count=0,
            details=[JobActionResponse(
                job_id="all",
                status="resumed",
                message=f"Se reanudaron {resumed_count} jobs pausados"
            )]
        )
        
    except Exception as e:
        db.rollback()
        raise e

@router.post("/bulk-stop", response_model=BulkJobActionResponse)
async def bulk_stop_jobs(request: BulkJobActionRequest, db: Session = Depends(get_db)):
    """
    Detiene múltiples jobs específicos.
    
    - **job_ids**: Lista de IDs de jobs a detener
    """
    success_count = 0
    failed_count = 0
    details = []
    
    try:
        for job_id in request.job_ids:
            try:
                # Buscar el job en la base de datos
                queue_item = db.query(ScrapingQueue).filter_by(job_id=job_id).first()
                
                # Si no se encuentra el job, registrar error
                if not queue_item:
                    details.append(JobActionResponse(
                        job_id=job_id,
                        status="failed",
                        message=f"Job '{job_id}' no encontrado"
                    ))
                    failed_count += 1
                    continue
                
                # Verificar que el job esté en un estado que se pueda detener
                if queue_item.status not in ["pending", "processing", "paused"]:
                    details.append(JobActionResponse(
                        job_id=job_id,
                        status="failed",
                        message=f"No se puede detener un job en estado '{queue_item.status}'"
                    ))
                    failed_count += 1
                    continue
                
                # Actualizar el estado a 'cancelled'
                queue_item.status = "cancelled"
                db.commit()
                
                details.append(JobActionResponse(
                    job_id=job_id,
                    status="stopped",
                    message=f"Job '{job_id}' detenido exitosamente"
                ))
                success_count += 1
                
            except Exception as e:
                details.append(JobActionResponse(
                    job_id=job_id,
                    status="failed",
                    message=f"Error al detener job '{job_id}': {str(e)}"
                ))
                failed_count += 1
        
        return BulkJobActionResponse(
            success_count=success_count,
            failed_count=failed_count,
            details=details
        )
        
    except Exception as e:
        db.rollback()
        raise e

@router.post("/bulk-pause", response_model=BulkJobActionResponse)
async def bulk_pause_jobs(request: BulkJobActionRequest, db: Session = Depends(get_db)):
    """
    Pausa múltiples jobs específicos.
    
    - **job_ids**: Lista de IDs de jobs a pausar
    """
    success_count = 0
    failed_count = 0
    details = []
    
    try:
        for job_id in request.job_ids:
            try:
                # Buscar el job en la base de datos
                queue_item = db.query(ScrapingQueue).filter_by(job_id=job_id).first()
                
                # Si no se encuentra el job, registrar error
                if not queue_item:
                    details.append(JobActionResponse(
                        job_id=job_id,
                        status="failed",
                        message=f"Job '{job_id}' no encontrado"
                    ))
                    failed_count += 1
                    continue
                
                # Verificar que el job esté en un estado que se pueda pausar
                if queue_item.status not in ["pending", "processing"]:
                    details.append(JobActionResponse(
                        job_id=job_id,
                        status="failed",
                        message=f"No se puede pausar un job en estado '{queue_item.status}'"
                    ))
                    failed_count += 1
                    continue
                
                # Actualizar el estado a 'paused'
                queue_item.status = "paused"
                db.commit()
                
                details.append(JobActionResponse(
                    job_id=job_id,
                    status="paused",
                    message=f"Job '{job_id}' pausado exitosamente"
                ))
                success_count += 1
                
            except Exception as e:
                details.append(JobActionResponse(
                    job_id=job_id,
                    status="failed",
                    message=f"Error al pausar job '{job_id}': {str(e)}"
                ))
                failed_count += 1
        
        return BulkJobActionResponse(
            success_count=success_count,
            failed_count=failed_count,
            details=details
        )
        
    except Exception as e:
        db.rollback()
        raise e

@router.post("/bulk-resume", response_model=BulkJobActionResponse)
async def bulk_resume_jobs(request: BulkJobActionRequest, db: Session = Depends(get_db)):
    """
    Reanuda múltiples jobs específicos.
    
    - **job_ids**: Lista de IDs de jobs a reanudar
    """
    success_count = 0
    failed_count = 0
    details = []
    
    try:
        for job_id in request.job_ids:
            try:
                # Buscar el job en la base de datos
                queue_item = db.query(ScrapingQueue).filter_by(job_id=job_id).first()
                
                # Si no se encuentra el job, registrar error
                if not queue_item:
                    details.append(JobActionResponse(
                        job_id=job_id,
                        status="failed",
                        message=f"Job '{job_id}' no encontrado"
                    ))
                    failed_count += 1
                    continue
                
                # Verificar que el job esté en un estado que se pueda reanudar
                if queue_item.status != "paused":
                    details.append(JobActionResponse(
                        job_id=job_id,
                        status="failed",
                        message=f"No se puede reanudar un job en estado '{queue_item.status}'"
                    ))
                    failed_count += 1
                    continue
                
                # Actualizar el estado a 'pending'
                queue_item.status = "pending"
                db.commit()
                
                details.append(JobActionResponse(
                    job_id=job_id,
                    status="resumed",
                    message=f"Job '{job_id}' reanudado exitosamente"
                ))
                success_count += 1
                
            except Exception as e:
                details.append(JobActionResponse(
                    job_id=job_id,
                    status="failed",
                    message=f"Error al reanudar job '{job_id}': {str(e)}"
                ))
                failed_count += 1
        
        return BulkJobActionResponse(
            success_count=success_count,
            failed_count=failed_count,
            details=details
        )
        
    except Exception as e:
        db.rollback()
        raise e