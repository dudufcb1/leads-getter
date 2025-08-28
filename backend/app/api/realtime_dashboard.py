"""
Endpoints para panel de estadísticas en tiempo real.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database.database import get_db
from ..database.models import Website, Email, ScrapingQueue, ScrapingSession
from ..core.auth import get_current_active_user
from datetime import datetime, timedelta

router = APIRouter()

class RealTimeMetrics(BaseModel):
    """Métricas en tiempo real."""
    active_sessions: int
    processing_jobs: int
    pending_jobs: int
    completed_jobs: int
    failed_jobs: int
    emails_found_last_hour: int
    websites_processed_last_hour: int
    average_response_time: float
    system_load: float

class JobProgress(BaseModel):
    """Progreso de un job."""
    job_id: str
    url: str
    status: str
    progress: int
    total_items: int
    processed_items: int
    estimated_completion: str

class DashboardData(BaseModel):
    """Datos para el panel de control."""
    metrics: RealTimeMetrics
    active_jobs: List[JobProgress]
    top_domains: List[Dict[str, Any]]
    recent_websites: List[Dict[str, Any]]

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_active_user)
):
    """
    Obtiene datos para el panel de control en tiempo real.
    
    - **db**: Sesión de base de datos
    - **current_user**: Usuario actual
    """
    try:
        # Métricas en tiempo real
        active_sessions = db.query(func.count(ScrapingSession.id)).filter(
            ScrapingSession.status == "running"
        ).scalar() or 0
        
        processing_jobs = db.query(func.count(ScrapingQueue.id)).filter(
            ScrapingQueue.status == "processing"
        ).scalar() or 0
        
        pending_jobs = db.query(func.count(ScrapingQueue.id)).filter(
            ScrapingQueue.status == "pending"
        ).scalar() or 0
        
        completed_jobs = db.query(func.count(ScrapingQueue.id)).filter(
            ScrapingQueue.status == "completed"
        ).scalar() or 0
        
        failed_jobs = db.query(func.count(ScrapingQueue.id)).filter(
            ScrapingQueue.status == "failed"
        ).scalar() or 0
        
        # Emails encontrados en la última hora
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        emails_last_hour = db.query(func.count(Email.id)).filter(
            Email.created_at >= one_hour_ago
        ).scalar() or 0
        
        # Sitios web procesados en la última hora
        websites_last_hour = db.query(func.count(Website.id)).filter(
            Website.created_at >= one_hour_ago
        ).scalar() or 0
        
        # Tiempo promedio de respuesta (simulado)
        average_response_time = 1250.5  # ms
        
        # Carga del sistema (simulado)
        system_load = 0.65
        
        metrics = RealTimeMetrics(
            active_sessions=active_sessions,
            processing_jobs=processing_jobs,
            pending_jobs=pending_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            emails_found_last_hour=emails_last_hour,
            websites_processed_last_hour=websites_last_hour,
            average_response_time=average_response_time,
            system_load=system_load
        )
        
        # Jobs activos
        active_jobs_raw = db.query(ScrapingQueue).filter(
            ScrapingQueue.status.in_(["processing", "pending"])
        ).order_by(ScrapingQueue.created_at.desc()).limit(10).all()
        
        active_jobs = []
        for job in active_jobs_raw:
            # Calcular tiempo estimado de finalización (simplificado)
            if job.total_items > 0 and job.processed_items > 0:
                progress_ratio = job.processed_items / job.total_items
                estimated_completion = f"{int(progress_ratio * 10)}% completado"
            else:
                estimated_completion = "Calculando..."
            
            active_jobs.append(JobProgress(
                job_id=job.job_id,
                url=job.url,
                status=job.status,
                progress=job.progress,
                total_items=job.total_items,
                processed_items=job.processed_items,
                estimated_completion=estimated_completion
            ))
        
        # Dominios más comunes
        top_domains_raw = db.query(
            Website.domain,
            func.count(Website.id).label('count')
        ).group_by(Website.domain).order_by(func.count(Website.id).desc()).limit(5).all()
        
        top_domains = [
            {"domain": domain, "count": count}
            for domain, count in top_domains_raw
        ]
        
        # Sitios web recientes
        recent_websites_raw = db.query(Website).order_by(
            Website.created_at.desc()
        ).limit(10).all()
        
        recent_websites = []
        for website in recent_websites_raw:
            recent_websites.append({
                "id": website.id,
                "url": website.url,
                "domain": website.domain,
                "status": website.status,
                "quality_score": website.quality_score,
                "email_count": website.email_count,
                "created_at": website.created_at.isoformat() if website.created_at else None
            })
        
        return DashboardData(
            metrics=metrics,
            active_jobs=active_jobs,
            top_domains=top_domains,
            recent_websites=recent_websites
        )
        
    except Exception as e:
        raise e

@router.get("/metrics/stream")
async def stream_metrics(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_active_user)
):
    """
    Transmite métricas en tiempo real (simulado).
    
    - **db**: Sesión de base de datos
    - **current_user**: Usuario actual
    """
    # Esta sería una implementación de streaming en tiempo real
    # Para simplificar, devolvemos datos estáticos
    # En una implementación real, se usaría WebSockets o Server-Sent Events
    
    active_sessions = db.query(func.count(ScrapingSession.id)).filter(
        ScrapingSession.status == "running"
    ).scalar() or 0
    
    processing_jobs = db.query(func.count(ScrapingQueue.id)).filter(
        ScrapingQueue.status == "processing"
    ).scalar() or 0
    
    return {
        "active_sessions": active_sessions,
        "processing_jobs": processing_jobs,
        "timestamp": datetime.utcnow().isoformat()
    }