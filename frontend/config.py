"""
Configuración para el frontend de la aplicación.
"""

class FrontendConfig:
    """Configuración del frontend."""
    
    # URL base de la API
    API_BASE_URL = "http://127.0.0.1:8000/api/v1"
    
    # Configuración de la aplicación
    APP_TITLE = "Leads Generator - Panel de Control"
    APP_WIDTH = 1200
    APP_HEIGHT = 800
    
    # Configuración de colores
    PRIMARY_COLOR = "#2c3e50"
    SECONDARY_COLOR = "#3498db"
    SUCCESS_COLOR = "#27ae60"
    WARNING_COLOR = "#f39c12"
    DANGER_COLOR = "#e74c3c"
    LIGHT_COLOR = "#ecf0f1"
    DARK_COLOR = "#34495e"
    
    # Configuración de scraping por defecto
    DEFAULT_DEPTH = 3
    DEFAULT_DELAY = 2.0
    DEFAULT_LANGUAGES = ["es", "en"]
    
    # Configuración de actualización
    STATS_REFRESH_INTERVAL = 5000  # 5 segundos
    LEADS_REFRESH_INTERVAL = 10000  # 10 segundos