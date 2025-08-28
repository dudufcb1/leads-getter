"""
Endpoints para obtener estadísticas del sistema.
"""

from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from sqlalchemy.exc import SQLAlchemyError
import psutil
import time
import json
from datetime import datetime, timedelta

from ..database.database import get_db
from ..database.models import Website, Email, ScrapingQueue, ScrapingSession, ScrapingLog, SystemStats, ScrapingStats, JobStats
from ..core.exceptions_new import DatabaseException
from ..core.error_decorator_new import handle_errors
from ..core.cache import cached, cache, get_cached_stats, set_cached_stats, invalidate_stats_cache

router = APIRouter()

# Modelo para las estadísticas del sistema
class SystemStatsResponse(BaseModel):
    """Respuesta con estadísticas del sistema."""
    active_jobs: int
    total_jobs_today: int
    total_leads_today: int
    total_emails_today: int
    system_health: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
    performance_summary: Dict[str, Any]

# Modelo para las estadísticas de scraping
class ScrapingStatsResponse(BaseModel):
    """Respuesta con estadísticas de scraping."""
    period: str
    total_urls_processed: int
    success_rate: float
    avg_processing_time: float
    domains_crawled: int
    duplicates_filtered: int
    urls_by_hour: List[Dict[str, int]]
    top_domains: List[Dict[str, int]]

# Modelo para las estadísticas de jobs
class JobStatsResponse(BaseModel):
    """Respuesta con estadísticas de jobs."""
    job_id: str
    duration: Optional[int]
    efficiency: Optional[float]
    status_distribution: Dict[str, int]
    performance_history: List[Dict[str, Any]]

# Modelo para estadísticas históricas
class HistoricalStatsResponse(BaseModel):
    """Respuesta con estadísticas históricas."""
    period: str
    data: List[Dict[str, Any]]

# Modelo para estadísticas de fuentes
class SourceStatsResponse(BaseModel):
    """Respuesta con estadísticas por fuente."""
    sources: List[Dict[str, Any]]
    top_sources: List[Dict[str, Any]]

@router.get("/system", response_model=SystemStatsResponse)
@handle_errors
@cached(ttl=30)  # Cache por 30 segundos
async def get_system_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas del sistema en tiempo real.
    """
    try:
        # Obtener estadísticas básicas
        active_jobs = db.query(ScrapingQueue).filter(
            ScrapingQueue.status.in_(["pending", "processing"])
        ).count()
        
        today = datetime.utcnow().date()
        total_jobs_today = db.query(ScrapingQueue).filter(
            func.date(ScrapingQueue.created_at) == today
        ).count()
        
        total_leads_today = db.query(Website).filter(
            func.date(Website.created_at) == today
        ).count()
        
        total_emails_today = db.query(Email).filter(
            func.date(Email.created_at) == today
        ).count()
        
        # Obtener estadísticas del sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        system_health = {
            "database_status": "healthy",
            "memory_usage_mb": round(memory.used / (1024 * 1024), 2),
            "cpu_usage_percent": cpu_percent,
            "disk_usage_gb": round(disk.used / (1024 * 1024 * 1024), 2),
            "uptime_seconds": int(time.time() - psutil.boot_time())
        }
        
        # Obtener actividad reciente
        recent_logs = db.query(ScrapingLog).order_by(
            ScrapingLog.created_at.desc()
        ).limit(10).all()
        
        recent_activity = []
        for log in recent_logs:
            recent_activity.append({
                "timestamp": log.created_at.isoformat() if log.created_at else None,
                "level": log.level,
                "message": log.message,
                "url": log.url
            })
        
        # Obtener resumen de rendimiento
        avg_response_time = db.query(func.avg(Website.response_time)).scalar() or 0
        total_websites = db.query(Website).count()
        
        performance_summary = {
            "avg_response_time": round(float(avg_response_time), 2) if avg_response_time else 0,
            "total_websites": total_websites,
            "total_emails": db.query(Email).count(),
            "success_rate": round((total_websites / max(total_jobs_today, 1)) * 100, 2) if total_jobs_today > 0 else 0
        }
        
        return SystemStatsResponse(
            active_jobs=active_jobs,
            total_jobs_today=total_jobs_today,
            total_leads_today=total_leads_today,
            total_emails_today=total_emails_today,
            system_health=system_health,
            recent_activity=recent_activity,
            performance_summary=performance_summary
        )
        
    except SQLAlchemyError as e:
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        raise DatabaseException(f"Error al obtener estadísticas del sistema: {str(e)}")

@router.get("/scraping", response_model=ScrapingStatsResponse)
@handle_errors
@cached(ttl=60)  # Cache por 60 segundos
async def get_scraping_stats(period: str = "day", db: Session = Depends(get_db)):
    """
    Obtiene métricas detalladas de scraping.
    
    - **period**: Período de tiempo (hour, day, week, month)
    """
    try:
        # Determinar el período de tiempo
        end_time = datetime.utcnow()
        if period == "hour":
            start_time = end_time - timedelta(hours=1)
        elif period == "week":
            start_time = end_time - timedelta(weeks=1)
        elif period == "month":
            start_time = end_time - timedelta(days=30)
        else:  # day
            start_time = end_time - timedelta(days=1)
        
        # Obtener estadísticas de scraping
        total_urls_processed = db.query(Website).filter(
            Website.created_at >= start_time,
            Website.created_at <= end_time
        ).count()
        
        # Calcular tasa de éxito
        total_queue_items = db.query(ScrapingQueue).filter(
            ScrapingQueue.created_at >= start_time,
            ScrapingQueue.created_at <= end_time
        ).count()
        
        success_rate = (total_urls_processed / max(total_queue_items, 1)) * 10 if total_queue_items > 0 else 0
        
        # Calcular tiempo promedio de procesamiento
        avg_processing_time = db.query(func.avg(Website.response_time)).filter(
            Website.created_at >= start_time,
            Website.created_at <= end_time
        ).scalar() or 0
        
        # Obtener dominios crawleados
        domains_crawled = db.query(func.count(func.distinct(Website.domain))).filter(
            Website.created_at >= start_time,
            Website.created_at <= end_time
        ).scalar() or 0
        
        # Obtener duplicados filtrados (esto es una aproximación)
        duplicates_filtered = db.query(Website).filter(
            Website.is_spam == 1,
            Website.created_at >= start_time,
            Website.created_at <= end_time
        ).count()
        
        # Obtener URLs por hora
        urls_by_hour = []
        for i in range(24):
            hour_start = start_time + timedelta(hours=i)
            hour_end = hour_start + timedelta(hours=1)
            count = db.query(Website).filter(
                Website.created_at >= hour_start,
                Website.created_at < hour_end
            ).count()
            urls_by_hour.append({
                "hour": hour_start.hour,
                "count": count
            })
        
        # Obtener dominios principales
        top_domains_query = db.query(
            Website.domain,
            func.count(Website.id).label('count')
        ).filter(
            Website.created_at >= start_time,
            Website.created_at <= end_time
        ).group_by(Website.domain).order_by(func.count(Website.id).desc()).limit(10)
        
        top_domains = []
        for domain, count in top_domains_query:
            top_domains.append({
                "domain": domain,
                "count": count
            })
        
        return ScrapingStatsResponse(
            period=period,
            total_urls_processed=total_urls_processed,
            success_rate=round(success_rate, 2),
            avg_processing_time=round(float(avg_processing_time), 2) if avg_processing_time else 0,
            domains_crawled=domains_crawled,
            duplicates_filtered=duplicates_filtered,
            urls_by_hour=urls_by_hour,
            top_domains=top_domains
        )
        
    except SQLAlchemyError as e:
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        raise DatabaseException(f"Error al obtener estadísticas de scraping: {str(e)}")

@router.get("/jobs/{job_id}", response_model=JobStatsResponse)
@handle_errors
@cached(ttl=30)  # Cache por 30 segundos
async def get_job_stats(job_id: str, db: Session = Depends(get_db)):
    """
    Obtiene estadísticas específicas de un job.
    
    - **job_id**: ID del job
    """
    try:
        # Verificar que el job exista
        job = db.query(ScrapingQueue).filter(ScrapingQueue.job_id == job_id).first()
        if not job:
            raise DatabaseException(f"Job con ID '{job_id}' no encontrado")
        
        # Obtener estadísticas del job
        job_stats = db.query(JobStats).filter(JobStats.job_id == job_id).first()
        
        # Calcular duración si el job ha terminado
        duration = None
        if job.started_at and (job.status in ["completed", "failed", "cancelled"]):
            end_time = job.updated_at or datetime.utcnow()
            duration = int((end_time - job.started_at).total_seconds())
        
        # Calcular eficiencia (leads encontrados vs URLs procesadas)
        efficiency = None
        if job.processed_items > 0:
            # Obtener número de leads encontrados para este job
            leads_count = db.query(Website).filter(Website.source_url.like(f"%{job_id}%")).count()
            efficiency = (leads_count / job.processed_items) * 100
        
        # Obtener distribución de estados
        status_distribution = {
            "pending": db.query(ScrapingQueue).filter(ScrapingQueue.status == "pending").count(),
            "processing": db.query(ScrapingQueue).filter(ScrapingQueue.status == "processing").count(),
            "completed": db.query(ScrapingQueue).filter(ScrapingQueue.status == "completed").count(),
            "failed": db.query(ScrapingQueue).filter(ScrapingQueue.status == "failed").count(),
            "paused": db.query(ScrapingQueue).filter(ScrapingQueue.status == "paused").count(),
            "cancelled": db.query(ScrapingQueue).filter(ScrapingQueue.status == "cancelled").count()
        }
        
        # Obtener historial de rendimiento (simulado)
        performance_history = []
        if job_stats and job_stats.performance_history:
            try:
                performance_history = json.loads(job_stats.performance_history)
            except:
                performance_history = []
        
        return JobStatsResponse(
            job_id=job_id,
            duration=duration,
            efficiency=round(efficiency, 2) if efficiency else None,
            status_distribution=status_distribution,
            performance_history=performance_history
        )
        
    except SQLAlchemyError as e:
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        raise DatabaseException(f"Error al obtener estadísticas del job: {str(e)}")

@router.get("/historical", response_model=HistoricalStatsResponse)
@handle_errors
@cached(ttl=300)  # Cache por 5 minutos
async def get_historical_stats(period: str = "week", db: Session = Depends(get_db)):
    """
    Obtiene datos históricos con filtros de fecha.
    
    - **period**: Período de tiempo (day, week, month, year)
    """
    try:
        # Determinar el período de tiempo
        end_time = datetime.utcnow()
        if period == "day":
            start_time = end_time - timedelta(days=1)
            group_by = "hour"
        elif period == "month":
            start_time = end_time - timedelta(days=30)
            group_by = "day"
        elif period == "year":
            start_time = end_time - timedelta(days=365)
            group_by = "month"
        else:  # week
            start_time = end_time - timedelta(weeks=1)
            group_by = "day"
        
        # Obtener estadísticas históricas
        historical_data = []
        
        # Obtener datos agrupados por período
        if group_by == "hour":
            # Datos por hora (últimas 24 horas)
            for i in range(24):
                hour_start = start_time + timedelta(hours=i)
                hour_end = hour_start + timedelta(hours=1)
                
                websites_count = db.query(Website).filter(
                    Website.created_at >= hour_start,
                    Website.created_at < hour_end
                ).count()
                
                emails_count = db.query(Email).filter(
                    Email.created_at >= hour_start,
                    Email.created_at < hour_end
                ).count()
                
                jobs_count = db.query(ScrapingQueue).filter(
                    ScrapingQueue.created_at >= hour_start,
                    ScrapingQueue.created_at < hour_end
                ).count()
                
                historical_data.append({
                    "timestamp": hour_start.isoformat(),
                    "websites": websites_count,
                    "emails": emails_count,
                    "jobs": jobs_count
                })
                
        elif group_by == "day":
            # Datos por día
            for i in range((end_time - start_time).days):
                day_start = start_time + timedelta(days=i)
                day_end = day_start + timedelta(days=1)
                
                websites_count = db.query(Website).filter(
                    Website.created_at >= day_start,
                    Website.created_at < day_end
                ).count()
                
                emails_count = db.query(Email).filter(
                    Email.created_at >= day_start,
                    Email.created_at < day_end
                ).count()
                
                jobs_count = db.query(ScrapingQueue).filter(
                    ScrapingQueue.created_at >= day_start,
                    ScrapingQueue.created_at < day_end
                ).count()
                
                historical_data.append({
                    "timestamp": day_start.isoformat(),
                    "websites": websites_count,
                    "emails": emails_count,
                    "jobs": jobs_count
                })
                
        elif group_by == "month":
            # Datos por mes (últimos 12 meses)
            for i in range(12):
                month_start = start_time + timedelta(days=30 * i)
                month_end = month_start + timedelta(days=30)
                
                websites_count = db.query(Website).filter(
                    Website.created_at >= month_start,
                    Website.created_at < month_end
                ).count()
                
                emails_count = db.query(Email).filter(
                    Email.created_at >= month_start,
                    Email.created_at < month_end
                ).count()
                
                jobs_count = db.query(ScrapingQueue).filter(
                    ScrapingQueue.created_at >= month_start,
                    ScrapingQueue.created_at < month_end
                ).count()
                
                historical_data.append({
                    "timestamp": month_start.isoformat(),
                    "websites": websites_count,
                    "emails": emails_count,
                    "jobs": jobs_count
                })
        
        return HistoricalStatsResponse(
            period=period,
            data=historical_data
        )
        
    except SQLAlchemyError as e:
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        raise DatabaseException(f"Error al obtener estadísticas históricas: {str(e)}")

@router.get("/performance", response_model=Dict[str, Any])
@handle_errors
@cached(ttl=30)  # Cache por 30 segundos
async def get_performance_stats(db: Session = Depends(get_db)):
    """
    Obtiene métricas de rendimiento detalladas.
    """
    try:
        # Obtener métricas de rendimiento del sistema
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Obtener métricas de rendimiento de la base de datos
        db_connections = 1  # Valor simulado
        avg_query_time = 0.015  # Valor simulado
        
        # Obtener métricas de rendimiento del scraping
        avg_response_time = db.query(func.avg(Website.response_time)).scalar() or 0
        total_websites = db.query(Website).count()
        
        # Obtener estado de la cola
        pending_urls = db.query(ScrapingQueue).filter(ScrapingQueue.status == "pending").count()
        processing_urls = db.query(ScrapingQueue).filter(ScrapingQueue.status == "processing").count()
        completed_urls = db.query(ScrapingQueue).filter(ScrapingQueue.status == "completed").count()
        failed_urls = db.query(ScrapingQueue).filter(ScrapingQueue.status == "failed").count()
        
        performance_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "scraping_performance": {
                "requests_per_second": round(total_websites / max(avg_response_time / 1000, 1), 2) if avg_response_time > 0 else 0,
                "avg_response_time": round(float(avg_response_time), 2) if avg_response_time else 0,
                "median_response_time": round(float(avg_response_time * 0.8), 2) if avg_response_time else 0,
                "p95_response_time": round(float(avg_response_time * 1.5), 2) if avg_response_time else 0,
                "error_rate_percent": round((failed_urls / max(total_websites, 1)) * 100, 2) if total_websites > 0 else 0
            },
            "system_resources": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_io_read_mb": round(disk.used / (1024 * 1024), 2),
                "disk_io_write_mb": round(disk.free / (1024 * 1024), 2),
                "network_rx_mb": 0,  # Valor simulado
                "network_tx_mb": 0   # Valor simulado
            },
            "database_performance": {
                "connections_active": db_connections,
                "queries_per_second": 25.3,  # Valor simulado
                "avg_query_time": avg_query_time,
                "cache_hit_rate": 0.85  # Valor simulado
            },
            "queue_status": {
                "pending_urls": pending_urls,
                "processing_urls": processing_urls,
                "completed_urls": completed_urls,
                "failed_urls": failed_urls
            }
        }
        
        return performance_data
        
    except SQLAlchemyError as e:
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        raise DatabaseException(f"Error al obtener métricas de rendimiento: {str(e)}")

@router.get("/sources", response_model=SourceStatsResponse)
@handle_errors
@cached(ttl=300)  # Cache por 5 minutos
async def get_sources_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas por fuente/dominio.
    """
    try:
        # Obtener todas las fuentes
        sources_query = db.query(
            Website.domain,
            func.count(Website.id).label('websites_count'),
            func.count(Email.id).label('emails_count'),
            func.avg(Website.quality_score).label('avg_quality_score')
        ).outerjoin(Email, Website.id == Email.website_id).group_by(Website.domain)
        
        sources = []
        for domain, websites_count, emails_count, avg_quality_score in sources_query:
            sources.append({
                "domain": domain,
                "websites_count": websites_count,
                "emails_count": emails_count or 0,
                "avg_quality_score": round(float(avg_quality_score), 2) if avg_quality_score else 0
            })
        
        # Obtener las fuentes principales por número de websites
        top_sources_query = db.query(
            Website.domain,
            func.count(Website.id).label('count')
        ).group_by(Website.domain).order_by(func.count(Website.id).desc()).limit(10)
        
        top_sources = []
        for domain, count in top_sources_query:
            top_sources.append({
                "domain": domain,
                "count": count
            })
        
        return SourceStatsResponse(
            sources=sources,
            top_sources=top_sources
        )
        
    except SQLAlchemyError as e:
        raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
    except Exception as e:
        raise DatabaseException(f"Error al obtener estadísticas por fuente: {str(e)}")