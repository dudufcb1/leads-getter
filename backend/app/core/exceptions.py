"""
Módulo para excepciones personalizadas del sistema de generación de leads.
"""

from typing import Optional, Any, Dict
from fastapi import HTTPException, status


class LeadsGeneratorException(Exception):
    """Excepción base para el sistema de generación de leads."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_code = error_code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(LeadsGeneratorException):
    """Excepción para errores relacionados con la base de datos."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "DATABASE_ERROR", details)


class ScrapingException(LeadsGeneratorException):
    """Excepción para errores relacionados con el scraping."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "SCRAPING_ERROR", details)


class ValidationException(LeadsGeneratorException):
    """Excepción para errores de validación."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        error_details = details or {}
        if field:
            error_details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", error_details)


class NotFoundException(LeadsGeneratorException):
    """Excepción para recursos no encontrados."""
    
    def __init__(self, resource: str, identifier: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} no encontrado"
        if identifier:
            message += f" con ID: {identifier}"
        error_details = details or {}
        if identifier:
            error_details["identifier"] = identifier
        super().__init__(message, "NOT_FOUND", error_details)


class ConflictException(LeadsGeneratorException):
    """Excepción para conflictos en la creación o actualización de recursos."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "CONFLICT", details)


class UnauthorizedException(LeadsGeneratorException):
    """Excepción para acceso no autorizado."""
    
    def __init__(self, message: str = "No autorizado", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "UNAUTHORIZED", details)


class ForbiddenException(LeadsGeneratorException):
    """Excepción para acceso prohibido."""
    
    def __init__(self, message: str = "Acceso prohibido", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "FORBIDDEN", details)


def http_exception_handler(exc: LeadsGeneratorException) -> HTTPException:
    """
    Convierte una excepción personalizada en una HTTPException de FastAPI.
    
    Args:
        exc: La excepción personalizada
        
    Returns:
        HTTPException correspondiente
    """
    status_code_map = {
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "CONFLICT": status.HTTP_409_CONFLICT,
        "UNAUTHORIZED": status.HTTP_401_UNAUTHORIZED,
        "FORBIDDEN": status.HTTP_403_FORBIDDEN,
        "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "SCRAPING_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "UNKNOWN_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    
    status_code = status_code_map.get(exc.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )