"""
Manejador de errores personalizado para la API.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from typing import Optional
import logging
import traceback
import json

# Configurar logger
logger = logging.getLogger(__name__)

from .exceptions_new import (
    LeadsGeneratorException,
    DatabaseException,
    ScrapingException,
    ValidationException,
    NotFoundException,
    ConflictException,
    UnauthorizedException,
    ForbiddenException
)

class ErrorFormatter:
    """Clase para formatear respuestas de error consistentes."""
    
    @staticmethod
    def format_error(error_type: str, message: str, field: Optional[str] = None, path: Optional[str] = None, details: Optional[dict] = None) -> dict:
        """
        Formatea una respuesta de error consistente.
        
        Args:
            error_type: Tipo de error
            message: Mensaje de error
            field: Campo relacionado con el error (opcional)
            path: Ruta del endpoint (opcional)
            details: Detalles adicionales (opcional)
            
        Returns:
            Diccionario con la estructura de error
        """
        error_response = {
            "error": {
                "type": error_type,
                "message": message
            }
        }
        
        if field:
            error_response["error"]["field"] = field
            
        if path:
            error_response["error"]["path"] = path
            
        if details:
            error_response["error"]["details"] = details
            
        return error_response

def add_error_handlers(app: FastAPI):
    """
    Agrega manejadores de error personalizados a la aplicación FastAPI.
    
    - **app**: Aplicación FastAPI
    """
    
    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request: Request, exc: ValidationException):
        """Manejador para excepciones de validación."""
        logger.warning(f"Validation Exception: {exc.message}")
        
        field = exc.details.get("field") if exc.details else None
        
        return JSONResponse(
            status_code=400,
            content=ErrorFormatter.format_error(
                error_type="VALIDATION_ERROR",
                message=exc.message,
                field=field,
                path=request.url.path,
                details=exc.details
            )
        )
    
    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException):
        """Manejador para excepciones de recursos no encontrados."""
        logger.warning(f"Not Found Exception: {exc.message}")
        
        return JSONResponse(
            status_code=404,
            content=ErrorFormatter.format_error(
                error_type="NOT_FOUND",
                message=exc.message,
                path=request.url.path,
                details=exc.details
            )
        )
    
    @app.exception_handler(DatabaseException)
    async def database_exception_handler(request: Request, exc: DatabaseException):
        """Manejador para excepciones de base de datos."""
        logger.error(f"Database Exception: {exc.message}")
        
        return JSONResponse(
            status_code=500,
            content=ErrorFormatter.format_error(
                error_type="DATABASE_ERROR",
                message=exc.message,
                path=request.url.path,
                details=exc.details
            )
        )
    
    @app.exception_handler(ScrapingException)
    async def scraping_exception_handler(request: Request, exc: ScrapingException):
        """Manejador para excepciones de scraping."""
        logger.error(f"Scraping Exception: {exc.message}")
        
        return JSONResponse(
            status_code=500,
            content=ErrorFormatter.format_error(
                error_type="SCRAPING_ERROR",
                message=exc.message,
                path=request.url.path,
                details=exc.details
            )
        )
    
    @app.exception_handler(ConflictException)
    async def conflict_exception_handler(request: Request, exc: ConflictException):
        """Manejador para excepciones de conflictos."""
        logger.warning(f"Conflict Exception: {exc.message}")
        
        return JSONResponse(
            status_code=409,
            content=ErrorFormatter.format_error(
                error_type="CONFLICT",
                message=exc.message,
                path=request.url.path,
                details=exc.details
            )
        )
    
    @app.exception_handler(UnauthorizedException)
    async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
        """Manejador para excepciones de acceso no autorizado."""
        logger.warning(f"Unauthorized Exception: {exc.message}")
        
        return JSONResponse(
            status_code=401,
            content=ErrorFormatter.format_error(
                error_type="UNAUTHORIZED",
                message=exc.message,
                path=request.url.path,
                details=exc.details
            )
        )
    
    @app.exception_handler(ForbiddenException)
    async def forbidden_exception_handler(request: Request, exc: ForbiddenException):
        """Manejador para excepciones de acceso prohibido."""
        logger.warning(f"Forbidden Exception: {exc.message}")
        
        return JSONResponse(
            status_code=403,
            content=ErrorFormatter.format_error(
                error_type="FORBIDDEN",
                message=exc.message,
                path=request.url.path,
                details=exc.details
            )
        )
    
    @app.exception_handler(LeadsGeneratorException)
    async def leads_generator_exception_handler(request: Request, exc: LeadsGeneratorException):
        """Manejador general para excepciones personalizadas."""
        logger.error(f"LeadsGenerator Exception: {exc.message}")
        
        # Mapeo de códigos de error a códigos de estado HTTP
        status_code_map = {
            "VALIDATION_ERROR": 400,
            "NOT_FOUND": 404,
            "CONFLICT": 409,
            "UNAUTHORIZED": 401,
            "FORBIDDEN": 403,
            "DATABASE_ERROR": 500,
            "SCRAPING_ERROR": 500,
            "UNKNOWN_ERROR": 500,
        }
        
        status_code = status_code_map.get(exc.error_code, 500)
        
        return JSONResponse(
            status_code=status_code,
            content=ErrorFormatter.format_error(
                error_type=exc.error_code,
                message=exc.message,
                path=request.url.path,
                details=exc.details
            )
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Manejador general para todas las excepciones no manejadas."""
        logger.error(f"Unhandled Exception: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content=ErrorFormatter.format_error(
                error_type="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                path=request.url.path
            )
        )