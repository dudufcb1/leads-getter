"""
Items de Scrapy para el sistema de generación de leads.
"""

import scrapy


class LeadItem(scrapy.Item):
    """Item para leads encontrados."""
    # Campos básicos
    url = scrapy.Field()
    domain = scrapy.Field()
    language = scrapy.Field()
    status = scrapy.Field()
    depth_level = scrapy.Field()
    source_url = scrapy.Field()
    emails = scrapy.Field()  # Lista de emails encontrados
    
    # Campos avanzados de calidad
    page_quality_score = scrapy.Field()  # Puntuación de calidad de página (0-100)
    email_quality_score = scrapy.Field()  # Calidad promedio de emails (0-1)
    contact_score = scrapy.Field()  # Puntuación de información de contacto (0-100)
    content_type = scrapy.Field()  # Tipo de contenido detectado
    has_business_keywords = scrapy.Field()  # Lista de palabras clave de negocio encontradas
    
    # Campos de validación y filtrado
    is_spam = scrapy.Field()  # 1=spam, 0=no spam
    language_confidence = scrapy.Field()  # Confianza en detección de idioma (0-1)
    duplicate_hash = scrapy.Field()  # Hash para detectar duplicados
    fingerprint = scrapy.Field()  # Fingerprint único de la página
    
    # Campos de rendimiento y monitoreo
    load_time = scrapy.Field()  # Tiempo de carga en ms
    word_count = scrapy.Field()  # Número de palabras en la página
    link_count = scrapy.Field()  # Número de enlaces en la página
    image_count = scrapy.Field()  # Número de imágenes en la página
    
    # Metadata adicional
    title = scrapy.Field()  # Título de la página
    description = scrapy.Field()  # Descripción/meta description
    keywords = scrapy.Field()  # Palabras clave
    
    # Campos existentes en el modelo de base de datos
    response_time = scrapy.Field()  # Tiempo de respuesta en ms
    page_size = scrapy.Field()  # Tamaño de página en bytes
    http_status = scrapy.Field()  # Código de estado HTTP
    quality_score = scrapy.Field()  # Puntuación de calidad (0-100)
    email_count = scrapy.Field()  # Número de emails encontrados
    last_scraped = scrapy.Field()  # Última vez scrapeado
    scrape_count = scrapy.Field()  # Número de veces scrapeado
    error_count = scrapy.Field()  # Número de errores
    last_error = scrapy.Field()  # Último error
    user_agent = scrapy.Field()  # User-Agent usado
    ip_address = scrapy.Field()  # IP del servidor
    scraped_at = scrapy.Field()  # Timestamp de scraping
    email_context = scrapy.Field()  # Contexto donde se encontró cada email
    email_anchors = scrapy.Field()  # Texto del enlace para cada email


class EmailItem(scrapy.Item):
    """Item para emails encontrados."""
    email = scrapy.Field()
    source_page = scrapy.Field()
    website_url = scrapy.Field()