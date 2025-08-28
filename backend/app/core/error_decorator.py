"""
Decorador para manejo consistente de errores en endpoints de FastAPI.
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional
from sqlalchemy.exc import SQLAlchemyError
from .exceptions import (
    LeadsGeneratorException,
    DatabaseException,
    ScrapingException,
    ValidationException,
    NotFoundException
)

# Configurar logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Crear handler para el logger
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Evitar duplicados
logger.propagate = False


def handle_errors(func: Callable) -> Callable:
    """
    Decorador para manejo consistente de errores en endpoints.
    
    Args:
        func: La función a decorar
        
    Returns:
        La función decorada
    """
    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except LeadsGeneratorException:
            # Si ya es una excepción personalizada, relanzarla
            raise
        except SQLAlchemyError as e:
            # Manejar errores de base de datos
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise DatabaseException(f"Error al acceder a la base de datos: {str(e)}")
        except ValueError as e:
            # Manejar errores de validación
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            raise ValidationException(str(e))
        except FileNotFoundError as e:
            # Manejar errores de archivos no encontrados
            logger.warning(f"File not found in {func.__name__}: {str(e)}")
            raise NotFoundException("Archivo", str(e))
        except Exception as e:
            # Manejar cualquier otro error
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            raise ScrapingException(f"Error inesperado: {str(e)}")
    
    return wrapper