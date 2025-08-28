"""
Configuración del sistema para el generador de leads.
"""

import os
from typing import List, Dict, Any

class SystemConfig:
    """Clase para manejar la configuración del sistema."""
    
    def __init__(self):
        """Inicializa la configuración del sistema."""
        # Configuración de scraping
        self.max_depth = int(os.getenv("MAX_DEPTH", "3"))
        self.delay = float(os.getenv("DELAY", "2.0"))
        self.allowed_languages: List[str] = os.getenv("ALLOWED_LANGUAGES", "es,en").split(",")
        self.min_quality_score = int(os.getenv("MIN_QUALITY_SCORE", "30"))
        
        # Configuración de filtrado
        self.email_validation_enabled = os.getenv("EMAIL_VALIDATION_ENABLED", "true").lower() == "true"
        self.spam_filter_enabled = os.getenv("SPAM_FILTER_ENABLED", "true").lower() == "true"
        self.duplicate_filter_enabled = os.getenv("DUPLICATE_FILTER_ENABLED", "true").lower() == "true"
        self.business_relevance_filter_enabled = os.getenv("BUSINESS_RELEVANCE_FILTER_ENABLED", "true").lower() == "true"
        self.content_quality_filter_enabled = os.getenv("CONTENT_QUALITY_FILTER_ENABLED", "true").lower() == "true"
        
        # Configuración de base de datos
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./leads.db")
        self.database_pool_size = int(os.getenv("DATABASE_POOL_SIZE", "10"))
        self.database_max_overflow = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
        
        # Configuración de seguridad
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-here")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        
        # Configuración de logs
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "leads_generator.log")
        
        # Configuración de Scrapy
        self.scrapy_settings: Dict[str, Any] = {
            "USER_AGENT": os.getenv("USER_AGENT", "LeadsGeneratorBot/1.0"),
            "ROBOTSTXT_OBEY": os.getenv("ROBOTSTXT_OBEY", "true").lower() == "true",
            "CONCURRENT_REQUESTS": int(os.getenv("CONCURRENT_REQUESTS", "16")),
            "DOWNLOAD_DELAY": self.delay,
            "DEPTH_LIMIT": self.max_depth,
            "ALLOWED_LANGUAGES": self.allowed_languages,
            "LOG_LEVEL": self.log_level
        }
    
    def get_scrapy_settings(self) -> Dict[str, Any]:
        """
        Obtiene la configuración de Scrapy.
        
        Returns:
            Dict[str, Any]: Configuración de Scrapy
        """
        return self.scrapy_settings.copy()
    
    def update_config(self, config_dict: Dict[str, Any]) -> None:
        """
        Actualiza la configuración del sistema.
        
        - **config_dict**: Diccionario con la nueva configuración
        """
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Actualizar configuración de Scrapy
        if "delay" in config_dict:
            self.scrapy_settings["DOWNLOAD_DELAY"] = config_dict["delay"]
        if "max_depth" in config_dict:
            self.scrapy_settings["DEPTH_LIMIT"] = config_dict["max_depth"]
        if "allowed_languages" in config_dict:
            self.scrapy_settings["ALLOWED_LANGUAGES"] = config_dict["allowed_languages"]
        if "log_level" in config_dict:
            self.scrapy_settings["LOG_LEVEL"] = config_dict["log_level"]
    
    def get_config_dict(self) -> Dict[str, Any]:
        """
        Obtiene la configuración actual como diccionario.
        
        Returns:
            Dict[str, Any]: Configuración actual
        """
        return {
            "max_depth": self.max_depth,
            "delay": self.delay,
            "allowed_languages": self.allowed_languages,
            "min_quality_score": self.min_quality_score,
            "email_validation_enabled": self.email_validation_enabled,
            "spam_filter_enabled": self.spam_filter_enabled,
            "duplicate_filter_enabled": self.duplicate_filter_enabled,
            "business_relevance_filter_enabled": self.business_relevance_filter_enabled,
            "content_quality_filter_enabled": self.content_quality_filter_enabled,
            "database_url": self.database_url,
            "database_pool_size": self.database_pool_size,
            "database_max_overflow": self.database_max_overflow,
            "secret_key": self.secret_key,
            "algorithm": self.algorithm,
            "access_token_expire_minutes": self.access_token_expire_minutes,
            "log_level": self.log_level,
            "log_file": self.log_file
        }
    
    def reset_to_defaults(self) -> None:
        """Restablece la configuración a los valores por defecto."""
        # Crear una nueva instancia con valores por defecto
        default_config = SystemConfig()
        
        # Copiar los valores por defecto
        for key, value in default_config.get_config_dict().items():
            setattr(self, key, value)
        
        # Actualizar configuración de Scrapy
        self.scrapy_settings = default_config.get_scrapy_settings()

# Instancia global de configuración
config = SystemConfig()

# Exportar la configuración
__all__ = ["config", "SystemConfig"]