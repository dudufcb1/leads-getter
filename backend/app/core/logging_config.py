"""
Configuración del sistema de logging para la aplicación.
"""

import logging
import logging.config
import os
from typing import Dict, Any
from pathlib import Path
from .config import settings

# Asegurarse de que el directorio de logs exista
log_file_path = Path(settings.LOG_FILE_PATH)
log_file_path.parent.mkdir(parents=True, exist_ok=True)

# Configuración básica del logging
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "metrics": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(metrics)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(log_file_path),
            "maxBytes": 1024 * 1024 * 10, # 10 MB
            "backupCount": 5,
            "formatter": "detailed",
        },
        "metrics_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(log_file_path).replace(".log", "_metrics.log"),
            "maxBytes": 1024 * 1024 * 10, # 10 MB
            "backupCount": 5,
            "formatter": "metrics",
        },
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default", "file"],
            "level": settings.LOG_LEVEL,
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False,
        },
        "leads_generator": {
            "handlers": ["default", "file"],
            "level": settings.LOG_LEVEL,
            "propagate": False,
        },
        "leads_generator.metrics": {
            "handlers": ["metrics_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

def setup_logging():
    """Configura el sistema de logging."""
    # Asegurarse de que el directorio de logs exista
    log_file_path = Path(settings.LOG_FILE_PATH)
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configurar logging
    logging.config.dictConfig(LOGGING_CONFIG)