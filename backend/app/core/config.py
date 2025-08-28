"""
Configuración de la aplicación.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from .system_config import config


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic."""

    # Configuración del servidor
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    # Configuración de la base de datos
    DATABASE_URL: str = config.database_url

    # Configuración del scraper
    DEFAULT_DEPTH: int = config.max_depth
    DEFAULT_DELAY: float = config.delay
    DEFAULT_LANGUAGES: list = config.allowed_languages

    # Configuración de Scrapy
    USER_AGENT: str = config.scrapy_settings.get("USER_AGENT", "leads-generator (+https://github.com/your-repo/leads-generator)")
    DOWNLOAD_DELAY: float = config.delay
    CONCURRENT_REQUESTS: int = config.scrapy_settings.get("CONCURRENT_REQUESTS", 16)
    CONCURRENT_REQUESTS_PER_DOMAIN: int = config.scrapy_settings.get("CONCURRENT_REQUESTS_PER_DOMAIN", 8)

    # Configuración de logging
    LOG_LEVEL: str = config.log_level
    LOG_FILE_PATH: str = config.log_file

    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()