"""
Configuración de la aplicación.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación usando Pydantic."""

    # Configuración del servidor
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    # Configuración de la base de datos
    DATABASE_URL: str = f"sqlite:///{Path(__file__).parent.parent.parent / 'leads_generator.db'}"

    # Configuración del scraper
    DEFAULT_DEPTH: int = 3
    DEFAULT_DELAY: float = 2.0
    DEFAULT_LANGUAGES: list = ["es", "en"]

    # Configuración de Scrapy
    USER_AGENT: str = "leads-generator (+https://github.com/your-repo/leads-generator)"
    DOWNLOAD_DELAY: float = 1.0
    CONCURRENT_REQUESTS: int = 16
    CONCURRENT_REQUESTS_PER_DOMAIN: int = 8

    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()