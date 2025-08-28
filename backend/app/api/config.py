"""
Endpoints para configuración del sistema.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ..core.auth import is_admin_user
from ..core.config import settings

router = APIRouter()

class SystemConfig(BaseModel):
    """Modelo para la configuración del sistema."""
    max_depth: int = 3
    delay: float = 2.0
    allowed_languages: list[str] = ["es", "en"]
    min_quality_score: int = 30
    email_validation_enabled: bool = True
    spam_filter_enabled: bool = True
    duplicate_filter_enabled: bool = True

class UpdateConfigRequest(BaseModel):
    """Modelo para la solicitud de actualización de configuración."""
    config: Dict[str, Any]

class ConfigResponse(BaseModel):
    """Modelo para la respuesta de configuración."""
    config: Dict[str, Any]
    message: str

# Configuración en memoria (en producción, esto debería estar en una base de datos)
current_config = {
    "max_depth": 3,
    "delay": 2.0,
    "allowed_languages": ["es", "en"],
    "min_quality_score": 30,
    "email_validation_enabled": True,
    "spam_filter_enabled": True,
    "duplicate_filter_enabled": True
}

@router.get("/system", response_model=ConfigResponse)
async def get_system_config(current_user: str = Depends(is_admin_user)):
    """
    Obtiene la configuración actual del sistema.
    
    - **current_user**: Usuario actual (requiere permisos de administrador)
    """
    return ConfigResponse(
        config=current_config,
        message="System configuration retrieved successfully"
    )

@router.put("/system", response_model=ConfigResponse)
async def update_system_config(
    request: UpdateConfigRequest,
    current_user: str = Depends(is_admin_user)
):
    """
    Actualiza la configuración del sistema.
    
    - **request**: Nueva configuración
    - **current_user**: Usuario actual (requiere permisos de administrador)
    """
    global current_config
    
    # Validar y actualizar configuración
    for key, value in request.config.items():
        if key in current_config:
            # Validaciones específicas
            if key == "max_depth" and not isinstance(value, int):
                raise ValueError("max_depth must be an integer")
            if key == "delay" and not isinstance(value, (int, float)):
                raise ValueError("delay must be a number")
            if key == "allowed_languages" and not isinstance(value, list):
                raise ValueError("allowed_languages must be a list")
            if key in ["email_validation_enabled", "spam_filter_enabled", "duplicate_filter_enabled"] and not isinstance(value, bool):
                raise ValueError(f"{key} must be a boolean")
            
            current_config[key] = value
    
    return ConfigResponse(
        config=current_config,
        message="System configuration updated successfully"
    )

@router.get("/system/default", response_model=ConfigResponse)
async def get_default_config(current_user: str = Depends(is_admin_user)):
    """
    Obtiene la configuración por defecto del sistema.
    
    - **current_user**: Usuario actual (requiere permisos de administrador)
    """
    default_config = {
        "max_depth": 3,
        "delay": 2.0,
        "allowed_languages": ["es", "en"],
        "min_quality_score": 30,
        "email_validation_enabled": True,
        "spam_filter_enabled": True,
        "duplicate_filter_enabled": True
    }
    
    return ConfigResponse(
        config=default_config,
        message="Default system configuration retrieved successfully"
    )

@router.post("/system/reset", response_model=ConfigResponse)
async def reset_system_config(current_user: str = Depends(is_admin_user)):
    """
    Restablece la configuración del sistema a los valores por defecto.
    
    - **current_user**: Usuario actual (requiere permisos de administrador)
    """
    global current_config
    default_config = {
        "max_depth": 3,
        "delay": 2.0,
        "allowed_languages": ["es", "en"],
        "min_quality_score": 30,
        "email_validation_enabled": True,
        "spam_filter_enabled": True,
        "duplicate_filter_enabled": True
    }
    current_config = default_config.copy()
    
    return ConfigResponse(
        config=current_config,
        message="System configuration reset to default values"
    )

@router.get("/scrapy/settings", response_model=ConfigResponse)
async def get_scrapy_settings(current_user: str = Depends(is_admin_user)):
    """
    Obtiene la configuración de Scrapy.
    
    - **current_user**: Usuario actual (requiere permisos de administrador)
    """
    # Configuración de Scrapy
    scrapy_settings = {
        "USER_AGENT": "LeadsGeneratorBot/1.0",
        "ROBOTSTXT_OBEY": True,
        "CONCURRENT_REQUESTS": 16,
        "DOWNLOAD_DELAY": current_config["delay"],
        "DEPTH_LIMIT": current_config["max_depth"],
        "ALLOWED_LANGUAGES": current_config["allowed_languages"]
    }
    
    return ConfigResponse(
        config=scrapy_settings,
        message="Scrapy settings retrieved successfully"
    )