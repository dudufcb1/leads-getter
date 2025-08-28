"""
Integración del sistema de métricas con el sistema de logging.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from .metrics import collect_real_time_metrics
from ..database.database import get_db

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class MetricsLoggingHandler(logging.Handler):
    """Handler personalizado para registrar métricas en los logs."""
    
    def __init__(self):
        super().__init__()
        self.setLevel(logging.INFO)
    
    def emit(self, record):
        """Registra una entrada de log con métricas."""
        try:
            # Obtener métricas en tiempo real
            db = next(get_db())
            metrics = collect_real_time_metrics(db)
            
            # Agregar métricas al mensaje del log
            if hasattr(record, 'metrics'):
                record.metrics.update(metrics)
            else:
                record.metrics = metrics
                
            # Formatear el mensaje con las métricas
            msg = self.format(record)
            if record.metrics:
                msg += f" | Metrics: {record.metrics}"
                
            # Imprimir el mensaje
            print(msg)
        except Exception as e:
            # En caso de error, imprimir el mensaje original
            print(self.format(record))

def setup_metrics_logging():
    """Configura el logging para incluir métricas."""
    # Crear handler para métricas
    metrics_handler = MetricsLoggingHandler()
    
    # Configurar formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    metrics_handler.setFormatter(formatter)
    
    # Agregar handler al logger
    logger.addHandler(metrics_handler)
    
    # Evitar duplicados
    logger.propagate = False
    
    return logger

def log_metrics_event(event_type: str, details: Dict[str, Any] = None):
    """
    Registra un evento de métricas.
    
    Args:
        event_type: Tipo de evento
        details: Detalles adicionales del evento
    """
    if details is None:
        details = {}
        
    # Agregar timestamp
    details['timestamp'] = datetime.utcnow().isoformat()
    details['event_type'] = event_type
    
    # Registrar evento
    logger.info(f"Metrics event: {event_type}", extra={'metrics': details})

def log_system_metrics():
    """Registra métricas del sistema."""
    try:
        # Obtener métricas en tiempo real
        db = next(get_db())
        metrics = collect_real_time_metrics(db)
        
        # Registrar métricas
        logger.info("System metrics collected", extra={'metrics': metrics})
    except Exception as e:
        logger.error(f"Error collecting system metrics: {str(e)}")

def log_scraping_metrics(session_id: str = None):
    """Registra métricas de scraping."""
    try:
        # Obtener métricas en tiempo real
        db = next(get_db())
        metrics = collect_real_time_metrics(db)
        
        # Agregar información de sesión
        if session_id:
            metrics['session_id'] = session_id
            
        # Registrar métricas
        logger.info("Scraping metrics collected", extra={'metrics': metrics})
    except Exception as e:
        logger.error(f"Error collecting scraping metrics: {str(e)}")

def log_job_metrics(job_id: str):
    """Registra métricas de un job específico."""
    try:
        # Obtener métricas en tiempo real
        db = next(get_db())
        metrics = collect_real_time_metrics(db)
        
        # Agregar información de job
        metrics['job_id'] = job_id
            
        # Registrar métricas
        logger.info("Job metrics collected", extra={'metrics': metrics})
    except Exception as e:
        logger.error(f"Error collecting job metrics: {str(e)}")

# Inicializar logging de métricas
metrics_logger = setup_metrics_logging()