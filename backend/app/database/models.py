"""
Modelos de base de datos para el sistema de generación de leads.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Website(Base):
    """Modelo para almacenar información de sitios web únicos."""
    __tablename__ = "websites"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), unique=True, nullable=False, index=True)
    domain = Column(String(255), nullable=False, index=True)
    language = Column(String(10), nullable=True)
    status = Column(Enum("pending", "processed", "no_contact", "failed", "blocked", name="website_status"),
                    default="pending", nullable=False)
    depth_level = Column(Integer, default=0, nullable=False)
    source_url = Column(String(500), nullable=True)

    # Campos avanzados para scraping
    response_time = Column(Integer, nullable=True)  # Tiempo de respuesta en ms
    page_size = Column(Integer, nullable=True)  # Tamaño de página en bytes
    http_status = Column(Integer, nullable=True)  # Código de estado HTTP
    content_type = Column(String(100), nullable=True)  # Tipo de contenido
    quality_score = Column(Integer, default=0, nullable=False)  # Puntuación de calidad (0-100)
    email_count = Column(Integer, default=0, nullable=False)  # Número de emails encontrados
    last_scraped = Column(DateTime(timezone=True), nullable=True)  # Última vez scrapeado
    scrape_count = Column(Integer, default=0, nullable=False)  # Número de veces scrapeado
    error_count = Column(Integer, default=0, nullable=False)  # Número de errores
    last_error = Column(Text, nullable=True)  # Último error
    user_agent = Column(String(500), nullable=True)  # User-Agent usado
    ip_address = Column(String(45), nullable=True)  # IP del servidor

    # Metadata adicional
    title = Column(String(500), nullable=True)  # Título de la página
    description = Column(Text, nullable=True)  # Descripción/meta description
    keywords = Column(Text, nullable=True)  # Palabras clave

    # Campos avanzados de calidad y scoring
    page_quality_score = Column(Integer, default=0, nullable=False)  # Puntuación de calidad de página (0-100)
    email_quality_score = Column(Float, default=0.0, nullable=False)  # Calidad promedio de emails (0-1)
    contact_score = Column(Integer, default=0, nullable=False)  # Puntuación de información de contacto (0-100)
    content_type = Column(String(50), nullable=True)  # Tipo de contenido detectado
    has_business_keywords = Column(Text, nullable=True)  # JSON array de palabras clave encontradas

    # Campos de validación y filtrado
    is_spam = Column(Integer, default=0, nullable=False)  # 1=spam, 0=no spam
    language_confidence = Column(Float, default=0.0, nullable=False)  # Confianza en detección de idioma (0-1)
    duplicate_hash = Column(String(64), nullable=True)  # Hash para detectar duplicados
    fingerprint = Column(String(128), nullable=True)  # Fingerprint único de la página

    # Campos de rendimiento y monitoreo
    load_time = Column(Integer, nullable=True)  # Tiempo de carga en ms
    word_count = Column(Integer, default=0, nullable=False)  # Número de palabras en la página
    link_count = Column(Integer, default=0, nullable=False)  # Número de enlaces en la página
    image_count = Column(Integer, default=0, nullable=False)  # Número de imágenes en la página

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relación con emails
    emails = relationship("Email", back_populates="website", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Website(id={self.id}, url='{self.url}', status='{self.status}', quality={self.quality_score})>"


class Email(Base):
    """Modelo para almacenar correos electrónicos encontrados."""
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    source_page = Column(String(500), nullable=False)

    # Campos avanzados para calidad y validación
    is_valid = Column(Integer, default=1, nullable=False)  # 1=valid, 0=invalid
    quality_score = Column(Integer, default=50, nullable=False)  # Puntuación de calidad (0-100)
    validation_attempts = Column(Integer, default=0, nullable=False)  # Intentos de validación
    last_validated = Column(DateTime(timezone=True), nullable=True)  # Última validación
    email_type = Column(Enum("personal", "business", "noreply", "unknown", name="email_type"),
                       default="unknown", nullable=False)  # Tipo de email
    domain_quality = Column(Integer, default=50, nullable=False)  # Calidad del dominio (0-100)

    # Metadata adicional
    context = Column(Text, nullable=True)  # Contexto donde se encontró el email
    position = Column(Integer, nullable=True)  # Posición en la página
    anchor_text = Column(String(500), nullable=True)  # Texto del enlace si aplica

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relación con website
    website = relationship("Website", back_populates="emails")

    def __repr__(self):
        return f"<Email(id={self.id}, email='{self.email}', quality={self.quality_score}, valid={self.is_valid})>"


class ScrapingQueue(Base):
    """Modelo para gestionar la cola de URLs por procesar."""
    __tablename__ = "scraping_queue"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(500), unique=True, nullable=False, index=True)
    priority = Column(Integer, default=0, nullable=False, index=True)
    depth_level = Column(Integer, default=0, nullable=False)
    status = Column(Enum("pending", "processing", "completed", "failed", name="queue_status"),
                   default="pending", nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ScrapingQueue(id={self.id}, url='{self.url}', status='{self.status}')>"


class ScrapingSession(Base):
    """Modelo para rastrear sesiones de scraping."""
    __tablename__ = "scraping_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    start_url = Column(String(500), nullable=False)
    status = Column(Enum("running", "completed", "failed", "stopped", name="session_status"),
                    default="running", nullable=False)

    # Configuración de la sesión
    max_depth = Column(Integer, default=3, nullable=False)
    allowed_domains = Column(Text, nullable=True)  # JSON string de dominios permitidos
    user_agent = Column(String(500), nullable=True)
    delay = Column(Float, default=1.0, nullable=False)

    # Estadísticas de la sesión
    pages_processed = Column(Integer, default=0, nullable=False)
    emails_found = Column(Integer, default=0, nullable=False)
    errors_count = Column(Integer, default=0, nullable=False)
    avg_response_time = Column(Float, nullable=True)  # Tiempo promedio de respuesta

    # Control de tiempo
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration = Column(Integer, nullable=True)  # Duración en segundos

    # Configuración adicional
    settings = Column(Text, nullable=True)  # JSON string con configuración adicional

    def __repr__(self):
        return f"<ScrapingSession(id={self.id}, session_id='{self.session_id}', status='{self.status}')>"


class ScrapingLog(Base):
    """Modelo para logs detallados del proceso de scraping."""
    __tablename__ = "scraping_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    url = Column(String(500), nullable=False)
    level = Column(Enum("DEBUG", "INFO", "WARNING", "ERROR", name="log_level"),
                   default="INFO", nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(50), nullable=True)  # Categoría del log (spider, pipeline, middleware, etc.)
    log_metadata = Column(Text, nullable=True)  # JSON string con metadata adicional

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ScrapingLog(id={self.id}, level='{self.level}', url='{self.url}')>"