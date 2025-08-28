"""
Sistema de métricas en tiempo real para el sistema de generación de leads.
"""

import psutil
import time
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database.models import Website, Email, ScrapingQueue, SystemStats, ScrapingStats, JobStats
from ..database.database import get_db

class MetricsCollector:
    """Clase para recolectar métricas del sistema en tiempo real."""
    
    def __init__(self, db: Session):
        self.db = db
        self.last_collection_time = time.time()
        
    def collect_system_metrics(self) -> Dict[str, Any]:
        """Recolecta métricas del sistema."""
        try:
            # Obtener métricas del sistema
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Obtener métricas de la base de datos
            db_connections = 1  # Valor simulado
            db_queries_per_second = 25.3  # Valor simulado
            db_avg_query_time = 0.015  # Valor simulado
            
            # Obtener métricas de la cola de jobs
            queue_size = self.db.query(ScrapingQueue).count()
            active_jobs = self.db.query(ScrapingQueue).filter(
                ScrapingQueue.status.in_(["pending", "processing"])
            ).count()
            pending_jobs = self.db.query(ScrapingQueue).filter(
                ScrapingQueue.status == "pending"
            ).count()
            
            # Obtener tiempo de actividad
            uptime = int(time.time() - psutil.boot_time())
            
            metrics = {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": (disk.used / disk.total) * 100,
                "network_io": "{}",  # Valor simulado
                "db_connections": db_connections,
                "db_queries_per_second": db_queries_per_second,
                "db_avg_query_time": db_avg_query_time,
                "queue_size": queue_size,
                "active_jobs": active_jobs,
                "pending_jobs": pending_jobs,
                "uptime": uptime
            }
            
            # Guardar métricas en la base de datos
            system_stats = SystemStats(**metrics)
            self.db.add(system_stats)
            self.db.commit()
            
            return metrics
        except Exception as e:
            # En caso de error, devolver métricas básicas
            return {
                "cpu_usage": 0.0,
                "memory_usage": 0.0,
                "disk_usage": 0.0,
                "network_io": "{}",
                "db_connections": 0,
                "db_queries_per_second": 0.0,
                "db_avg_query_time": 0.0,
                "queue_size": 0,
                "active_jobs": 0,
                "pending_jobs": 0,
                "uptime": 0
            }
    
    def collect_scraping_metrics(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Recolecta métricas de scraping."""
        try:
            # Calcular velocidad de scraping (URLs por minuto)
            time_since_last_collection = time.time() - self.last_collection_time
            if time_since_last_collection > 0:
                # Obtener número de websites procesados desde la última recolección
                websites_count = self.db.query(Website).count()
                urls_per_minute = (websites_count / time_since_last_collection) * 60
            else:
                urls_per_minute = 0
            
            # Calcular tiempo promedio de procesamiento
            avg_processing_time = self.db.query(func.avg(Website.response_time)).scalar() or 0
            
            # Calcular tasa de éxito/fracaso
            total_websites = self.db.query(Website).count()
            failed_websites = self.db.query(Website).filter(Website.status == "failed").count()
            
            if total_websites > 0:
                success_rate = ((total_websites - failed_websites) / total_websites) * 100
                failure_rate = (failed_websites / total_websites) * 100
            else:
                success_rate = 0
                failure_rate = 0
            
            # Obtener estadísticas por dominio (simuladas)
            domain_stats = "{}"  # Valor simulado
            
            # Obtener estadísticas de duplicados
            duplicates_found = self.db.query(Website).filter(Website.is_spam == 1).count()
            duplicates_filtered = duplicates_found  # Aproximación
            
            metrics = {
                "urls_per_minute": urls_per_minute,
                "avg_processing_time": float(avg_processing_time) if avg_processing_time else 0,
                "success_rate": success_rate,
                "failure_rate": failure_rate,
                "domain_stats": domain_stats,
                "duplicates_found": duplicates_found,
                "duplicates_filtered": duplicates_filtered,
                "extra_metadata": "{}"
            }
            
            # Guardar métricas en la base de datos
            scraping_stats = ScrapingStats(
                session_id=session_id,
                **metrics
            )
            self.db.add(scraping_stats)
            self.db.commit()
            
            return metrics
        except Exception as e:
            # En caso de error, devolver métricas básicas
            return {
                "urls_per_minute": 0,
                "avg_processing_time": 0,
                "success_rate": 0,
                "failure_rate": 0,
                "domain_stats": "{}",
                "duplicates_found": 0,
                "duplicates_filtered": 0,
                "extra_metadata": "{}"
            }
    
    def collect_job_metrics(self, job_id: str) -> Dict[str, Any]:
        """Recolecta métricas de un job específico."""
        try:
            # Obtener el job
            job = self.db.query(ScrapingQueue).filter(ScrapingQueue.job_id == job_id).first()
            if not job:
                return {}
            
            # Calcular duración si el job ha terminado
            duration = None
            if job.started_at and (job.status in ["completed", "failed", "cancelled"]):
                end_time = job.updated_at or datetime.utcnow()
                duration = int((end_time - job.started_at).total_seconds())
            
            # Calcular eficiencia (leads encontrados vs URLs procesadas)
            efficiency = None
            if job.processed_items > 0:
                # Obtener número de leads encontrados para este job
                leads_count = self.db.query(Website).filter(Website.source_url.like(f"%{job_id}%")).count()
                efficiency = (leads_count / job.processed_items) * 100
            
            # Obtener distribución de estados (simulada)
            status_distribution = "{}"  # Valor simulado
            
            # Obtener historial de rendimiento (simulado)
            performance_history = "[]" # Valor simulado
            
            metrics = {
                "duration": duration,
                "efficiency": efficiency,
                "status_distribution": status_distribution,
                "performance_history": performance_history
            }
            
            # Guardar métricas en la base de datos
            job_stats = JobStats(
                job_id=job_id,
                **metrics
            )
            self.db.add(job_stats)
            self.db.commit()
            
            return metrics
        except Exception as e:
            # En caso de error, devolver métricas básicas
            return {
                "duration": None,
                "efficiency": None,
                "status_distribution": "{}",
                "performance_history": "[]"
            }
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Obtiene todas las métricas en tiempo real."""
        system_metrics = self.collect_system_metrics()
        scraping_metrics = self.collect_scraping_metrics()
        
        # Actualizar tiempo de última recolección
        self.last_collection_time = time.time()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": system_metrics,
            "scraping": scraping_metrics
        }

# Instancia global del colector de métricas
metrics_collector: Optional[MetricsCollector] = None

def get_metrics_collector(db: Session) -> MetricsCollector:
    """Obtiene una instancia del colector de métricas."""
    global metrics_collector
    if metrics_collector is None:
        metrics_collector = MetricsCollector(db)
    return metrics_collector

def collect_real_time_metrics(db: Session) -> Dict[str, Any]:
    """Recolecta métricas en tiempo real."""
    collector = get_metrics_collector(db)
    return collector.get_real_time_metrics()