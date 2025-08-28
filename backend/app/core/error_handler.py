"""
Manejador de errores personalizado para la API.
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional
import logging
import traceback

# Configurar logger
logger = logging.getLogger(__name__)

class CustomHTTPException(HTTPException):
    """Excepción HTTP personalizada con más detalles."""
    def __init__(self, status_code: int, detail: str, error_code: Optional[str] = None, field: Optional[str] = None):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.field = field

class DatabaseException(CustomHTTPException):
    """Excepción para errores de base de datos."""
    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(status_code=500, detail=detail, error_code="DATABASE_ERROR", field=field)

class ValidationException(CustomHTTPException):
    """Excepción para errores de validación."""
    def __init__(self, detail: str, field: Optional[str] = None):
        super().__init__(status_code=400, detail=detail, error_code="VALIDATION_ERROR", field=field)

class NotFoundException(CustomHTTPException):
    """Excepción para recursos no encontrados."""
    def __init__(self, resource: str, identifier: str):
        detail = f"{resource} with identifier '{identifier}' not found"
        super().__init__(status_code=404, detail=detail, error_code="NOT_FOUND", field=resource.lower())

class ScrapingException(CustomHTTPException):
    """Excepción para errores de scraping."""
    def __init__(self, detail: str):
        super().__init__(status_code=500, detail=detail, error_code="SCRAPING_ERROR")

class AuthenticationException(CustomHTTPException):
    """Excepción para errores de autenticación."""
    def __init__(self, detail: str):
        super().__init__(status_code=401, detail=detail, error_code="AUTHENTICATION_ERROR")

class AuthorizationException(CustomHTTPException):
    """Excepción para errores de autorización."""
    def __init__(self, detail: str):
        super().__init__(status_code=403, detail=detail, error_code="AUTHORIZATION_ERROR")

def add_error_handlers(app: FastAPI):
    """
    Agrega manejadores de error personalizados a la aplicación FastAPI.
    
    - **app**: Aplicación FastAPI
    """
    
    @app.exception_handler(CustomHTTPException)
    async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
        """Manejador para excepciones HTTP personalizadas."""
        logger.error(f"Custom HTTP Exception: {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": exc.error_code,
                    "message": exc.detail,
                    "field": exc.field,
                    "path": request.url.path
                }
            }
        )
    
    @app.exception_handler(DatabaseException)
    async def database_exception_handler(request: Request, exc: DatabaseException):
        """Manejador para excepciones de base de datos."""
        logger.error(f"Database Exception: {exc.detail}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "DATABASE_ERROR",
                    "message": exc.detail,
                    "field": exc.field,
                    "path": request.url.path
                }
            }
        )
    
    @app.exception_handler(ValidationException)
    async def validation_exception_handler(request: Request, exc: ValidationException):
        """Manejador para excepciones de validación."""
        logger.warning(f"Validation Exception: {exc.detail}")
        
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "type": "VALIDATION_ERROR",
                    "message": exc.detail,
                    "field": exc.field,
                    "path": request.url.path
                }
            }
        )
    
    @app.exception_handler(NotFoundException)
    async def not_found_exception_handler(request: Request, exc: NotFoundException):
        """Manejador para excepciones de recursos no encontrados."""
        logger.warning(f"Not Found Exception: {exc.detail}")
        
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "type": "NOT_FOUND",
                    "message": exc.detail,
                    "field": exc.field,
                    "path": request.url.path
                }
            }
        )
    
    @app.exception_handler(ScrapingException)
    async def scraping_exception_handler(request: Request, exc: ScrapingException):
        """Manejador para excepciones de scraping."""
        logger.error(f"Scraping Exception: {exc.detail}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "SCRAPING_ERROR",
                    "message": exc.detail,
                    "path": request.url.path
                }
            }
        )
    
    @app.exception_handler(AuthenticationException)
    async def authentication_exception_handler(request: Request, exc: AuthenticationException):
        """Manejador para excepciones de autenticación."""
        logger.warning(f"Authentication Exception: {exc.detail}")
        
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "type": "AUTHENTICATION_ERROR",
                    "message": exc.detail,
                    "path": request.url.path
                }
            }
        )
    
    @app.exception_handler(AuthorizationException)
    async def authorization_exception_handler(request: Request, exc: AuthorizationException):
        """Manejador para excepciones de autorización."""
        logger.warning(f"Authorization Exception: {exc.detail}")
        
        return JSONResponse(
            status_code=403,
            content={
                "error": {
                    "type": "AUTHORIZATION_ERROR",
                    "message": exc.detail,
                    "path": request.url.path
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Manejador general para todas las excepciones no manejadas."""
        logger.error(f"Unhandled Exception: {str(exc)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "path": request.url.path
                }
            }
        )

# Exportar las excepciones para uso en otros módulos
__all__ = [
    "CustomHTTPException",
    "DatabaseException",
    "ValidationException",
    "NotFoundException",
    "ScrapingException",
    "AuthenticationException",
    "AuthorizationException",
    "add_error_handlers"
]