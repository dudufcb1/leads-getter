"""
Endpoints avanzados para estadísticas del sistema.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from ..database.database import get_db
from ..database.models import Website, Email, ScrapingQueue, ScrapingSession, ScrapingLog
from ..core.exceptions import NotFoundException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

router = APIRouter()

class WebsiteStats(BaseModel):
    """Estadísticas de sitios web."""
    total_websites: int
    processed_websites: int
    failed_websites: int
    websites_with_emails: int
    average_quality_score: float

class EmailStats(BaseModel):
    """Estadísticas de emails."""
    total_emails: int
    unique_emails: int
    business_emails: int
    personal_emails: int
    average_quality_score: float

class JobStats(BaseModel):
    """Estadísticas de jobs."""
    total_jobs: int
    pending_jobs: int
    processing_jobs: int
    completed_jobs: int
    failed_jobs: int
    cancelled_jobs: int
    paused_jobs: int

class LanguageStats(BaseModel):
    """Estadísticas por idioma."""
    language: str
    count: int
    percentage: float

class ContentTypeStats(BaseModel):
    """Estadísticas por tipo de contenido."""
    content_type: str
    count: int
    percentage: float

class AdvancedStatsResponse(BaseModel):
    """Respuesta para estadísticas avanzadas."""
    websites: WebsiteStats
    emails: EmailStats
    jobs: JobStats
    languages: List[LanguageStats]
    content_types: List[ContentTypeStats]
    top_domains: List[Dict[str, Any]]
    scraping_trends: List[Dict[str, Any]]

class RealTimeStatsResponse(BaseModel):
    """Respuesta para estadísticas en tiempo real."""
    active_sessions: int
    processing_jobs: int
    emails_found_last_hour: int
    websites_processed_last_hour: int
    system_load: float
    memory_usage: float
    cpu_usage: float

@router.get("/advanced", response_model=AdvancedStatsResponse)
async def get_advanced_stats(
    days: int = Query(30, description="Número de días para calcular estadísticas"),
    db: Session = Depends(get_db)
):
    """
    Obtiene estadísticas avanzadas del sistema.
    
    - **days**: Número de días para calcular estadísticas (por defecto 30)
    """
    try:
        # Calcular fecha límite
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Estadísticas de sitios web
        total_websites = db.query(func.count(Website.id)).scalar()
        processed_websites = db.query(func.count(Website.id)).filter(
            Website.status == "processed"
        ).scalar()
        failed_websites = db.query(func.count(Website.id)).filter(
            Website.status == "failed"
        ).scalar()
        websites_with_emails = db.query(func.count(Website.id)).filter(
            Website.email_count > 0
        ).scalar()
        
        # Calcular puntuación promedio de calidad
        avg_quality_score = db.query(func.avg(Website.quality_score)).scalar() or 0
        
        website_stats = WebsiteStats(
            total_websites=total_websites,
            processed_websites=processed_websites,
            failed_websites=failed_websites,
            websites_with_emails=websites_with_emails,
            average_quality_score=round(float(avg_quality_score), 2)
        )
        
        # Estadísticas de emails
        total_emails = db.query(func.count(Email.id)).scalar()
        unique_emails = db.query(func.count(func.distinct(Email.email))).scalar()
        
        # Contar emails por tipo
        business_emails = db.query(func.count(Email.id)).filter(
            Email.email_type == "business"
        ).scalar()
        personal_emails = db.query(func.count(Email.id)).filter(
            Email.email_type == "personal"
        ).scalar()
        
        # Calcular puntuación promedio de calidad de emails
        avg_email_quality = db.query(func.avg(Email.quality_score)).scalar() or 0
        
        email_stats = EmailStats(
            total_emails=total_emails,
            unique_emails=unique_emails,
            business_emails=business_emails,
            personal_emails=personal_emails,
            average_quality_score=round(float(avg_email_quality), 2)
        )
        
        # Estadísticas de jobs
        total_jobs = db.query(func.count(ScrapingQueue.id)).scalar()
        pending_jobs = db.query(func.count(ScrapingQueue.id)).filter(
            ScrapingQueue.status == "pending"
        ).scalar()
        processing_jobs = db.query(func.count(ScrapingQueue.id)).filter(
            ScrapingQueue.status == "processing"
        ).scalar()
        completed_jobs = db.query(func.count(ScrapingQueue.id)).filter(
            ScrapingQueue.status == "completed"
        ).scalar()
        failed_jobs = db.query(func.count(ScrapingQueue.id)).filter(
            ScrapingQueue.status == "failed"
        ).scalar()
        cancelled_jobs = db.query(func.count(ScrapingQueue.id)).filter(
            ScrapingQueue.status == "cancelled"
        ).scalar()
        paused_jobs = db.query(func.count(ScrapingQueue.id)).filter(
            ScrapingQueue.status == "paused"
        ).scalar()
        
        job_stats = JobStats(
            total_jobs=total_jobs,
            pending_jobs=pending_jobs,
            processing_jobs=processing_jobs,
            completed_jobs=completed_jobs,
            failed_jobs=failed_jobs,
            cancelled_jobs=cancelled_jobs,
            paused_jobs=paused_jobs
        )
        
        # Estadísticas por idioma
        language_stats_raw = db.query(
            Website.language,
            func.count(Website.id).label('count')
        ).filter(
            Website.language.isnot(None)
        ).group_by(Website.language).all()
        
        total_with_language = sum([stat.count for stat in language_stats_raw])
        language_stats = []
        for stat in language_stats_raw:
            percentage = (stat.count / total_with_language * 100) if total_with_language > 0 else 0
            language_stats.append(LanguageStats(
                language=stat.language,
                count=stat.count,
                percentage=round(percentage, 2)
            ))
        
        # Estadísticas por tipo de contenido
        content_type_stats_raw = db.query(
            Website.content_type_detected,
            func.count(Website.id).label('count')
        ).filter(
            Website.content_type_detected.isnot(None)
        ).group_by(Website.content_type_detected).all()
        
        total_with_content_type = sum([stat.count for stat in content_type_stats_raw])
        content_type_stats = []
        for stat in content_type_stats_raw:
            percentage = (stat.count / total_with_content_type * 100) if total_with_content_type > 0 else 0
            content_type_stats.append(ContentTypeStats(
                content_type=stat.content_type_detected,
                count=stat.count,
                percentage=round(percentage, 2)
            ))
        
        # Dominios más comunes
        top_domains_raw = db.query(
            Website.domain,
            func.count(Website.id).label('count')
        ).group_by(Website.domain).order_by(func.count(Website.id).desc()).limit(10).all()
        
        top_domains = [
            {"domain": domain, "count": count}
            for domain, count in top_domains_raw
        ]
        
        # Tendencias de scraping (últimos 7 días)
        scraping_trends = []
        for i in range(7):
            date = datetime.utcnow() - timedelta(days=i)
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            websites_count = db.query(func.count(Website.id)).filter(
                and_(
                    Website.created_at >= start_date,
                    Website.created_at < end_date
                )
            ).scalar()
            
            emails_count = db.query(func.count(Email.id)).filter(
                and_(
                    Email.created_at >= start_date,
                    Email.created_at < end_date
                )
            ).scalar()
            
            scraping_trends.append({
                "date": start_date.isoformat(),
                "websites_processed": websites_count,
                "emails_found": emails_count
            })
        
        return AdvancedStatsResponse(
            websites=website_stats,
            emails=email_stats,
            jobs=job_stats,
            languages=language_stats,
            content_types=content_type_stats,
            top_domains=top_domains,
            scraping_trends=scraping_trends
        )
        
    except Exception as e:
        raise e

@router.get("/realtime", response_model=RealTimeStatsResponse)
async def get_realtime_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas en tiempo real del sistema.
    """
    try:
        # Sesiones activas
        active_sessions = db.query(func.count(ScrapingSession.id)).filter(
            ScrapingSession.status == "running"
        ).scalar()
        
        # Jobs en proceso
        processing_jobs = db.query(func.count(ScrapingQueue.id)).filter(
            ScrapingQueue.status == "processing"
        ).scalar()
        
        # Emails encontrados en la última hora
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        emails_last_hour = db.query(func.count(Email.id)).filter(
            Email.created_at >= one_hour_ago
        ).scalar()
        
        # Sitios web procesados en la última hora
        websites_last_hour = db.query(func.count(Website.id)).filter(
            Website.created_at >= one_hour_ago
        ).scalar()
        
        # Estadísticas del sistema (simuladas)
        system_load = 0.65  # Valor simulado
        memory_usage = 0.45  # Valor simulado
        cpu_usage = 0.32     # Valor simulado
        
        return RealTimeStatsResponse(
            active_sessions=active_sessions,
            processing_jobs=processing_jobs,
            emails_found_last_hour=emails_last_hour,
            websites_processed_last_hour=websites_last_hour,
            system_load=system_load,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage
        )
        
    except Exception as e:
        raise e

@router.get("/domain/{domain}", response_model=Dict[str, Any])
async def get_domain_stats(domain: str, db: Session = Depends(get_db)):
    """
    Obtiene estadísticas para un dominio específico.
    
    - **domain**: Dominio para obtener estadísticas
    """
    try:
        # Verificar si el dominio existe
        websites_count = db.query(func.count(Website.id)).filter(
            Website.domain == domain
        ).scalar()
        
        if websites_count == 0:
            raise NotFoundException("Dominio", identifier=domain)
        
        # Estadísticas del dominio
        total_websites = websites_count
        websites_with_emails = db.query(func.count(Website.id)).filter(
            and_(
                Website.domain == domain,
                Website.email_count > 0
            )
        ).scalar()
        
        # Emails del dominio
        emails = db.query(Email).join(Website).filter(
            Website.domain == domain
        ).all()
        
        total_emails = len(emails)
        unique_emails = len(set([email.email for email in emails]))
        
        # Calcular puntuación promedio
        if emails:
            avg_quality_score = sum([email.quality_score for email in emails]) / len(emails)
        else:
            avg_quality_score = 0
        
        # Tipos de emails
        email_types = {}
        for email in emails:
            email_type = email.email_type
            if email_type in email_types:
                email_types[email_type] += 1
            else:
                email_types[email_type] = 1
        
        return {
            "domain": domain,
            "total_websites": total_websites,
            "websites_with_emails": websites_with_emails,
            "total_emails": total_emails,
            "unique_emails": unique_emails,
            "average_quality_score": round(avg_quality_score, 2),
            "email_types": email_types
        }
        
    except Exception as e:
        raise e

@router.get("/job/{job_id}/detailed", response_model=Dict[str, Any])
async def get_detailed_job_stats(job_id: str, db: Session = Depends(get_db)):
    """
    Obtiene estadísticas detalladas para un job específico.
    
    - **job_id**: ID del job para obtener estadísticas
    """
    try:
        # Buscar el job
        job = db.query(ScrapingQueue).filter_by(job_id=job_id).first()
        if not job:
            raise NotFoundException("Job", identifier=job_id)
        
        # Logs del job
        logs = db.query(ScrapingLog).filter_by(session_id=job_id).order_by(
            ScrapingLog.created_at.desc()
        ).limit(50).all()
        
        # Contar logs por nivel
        log_levels = {}
        for log in logs:
            level = log.level
            if level in log_levels:
                log_levels[level] += 1
            else:
                log_levels[level] = 1
        
        # Últimos logs
        recent_logs = []
        for log in logs[:10]:
            recent_logs.append({
                "level": log.level,
                "message": log.message,
                "category": log.category,
                "timestamp": log.created_at.isoformat() if log.created_at else None
            })
        
        return {
            "job_id": job_id,
            "status": job.status,
            "progress": job.progress,
            "total_items": job.total_items,
            "processed_items": job.processed_items,
            "attempts": job.attempts,
            "log_summary": log_levels,
            "recent_logs": recent_logs
        }
        
    except Exception as e:
        raise e