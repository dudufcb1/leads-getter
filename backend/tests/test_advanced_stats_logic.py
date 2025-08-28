"""
Tests para la lógica de los endpoints de estadísticas usando devactivo.com como ejemplo.
"""

import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from sqlalchemy import and_
from datetime import datetime, timedelta
import sys
import os

# Añadir el directorio backend al path para resolver importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database.models import ScrapingQueue, Website, Email, Base

# Configurar base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_leads.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas en la base de datos de prueba
Base.metadata.create_all(bind=engine)

def setup_test_data():
    """Configura datos de prueba en la base de datos con devactivo.com como ejemplo."""
    db = TestingSessionLocal()
    
    # Limpiar datos previos
    db.query(ScrapingQueue).delete()
    db.query(Website).delete()
    db.query(Email).delete()
    
    # Crear jobs de prueba relacionados con devactivo.com
    jobs_data = [
        {
            "job_id": "devactivo_job_001",
            "url": "https://devactivo.com",
            "status": "completed",
            "priority": 0,
            "depth_level": 0,
            "attempts": 1,
            "total_items": 100,
            "processed_items": 100,
            "progress": 100
        },
        {
            "job_id": "devactivo_job_002",
            "url": "https://blog.devactivo.com",
            "status": "processing",
            "priority": 1,
            "depth_level": 1,
            "attempts": 2,
            "total_items": 50,
            "processed_items": 25,
            "progress": 50
        },
        {
            "job_id": "devactivo_job_003",
            "url": "https://docs.devactivo.com",
            "status": "pending",
            "priority": 2,
            "depth_level": 0,
            "attempts": 0,
            "total_items": 75,
            "processed_items": 0,
            "progress": 0
        }
    ]
    
    for job_data in jobs_data:
        job = ScrapingQueue(**job_data)
        db.add(job)
    
    db.commit()
    
    # Crear websites de prueba relacionados con devactivo.com
    websites_data = [
        {
            "url": "https://devactivo.com",
            "domain": "devactivo.com",
            "title": "DevActivo - Desarrollo de Software",
            "description": "Empresa especializada en desarrollo de software",
            "language": "es",
            "content_type_detected": "text/html",
            "response_time": 150.5,
            "status": "processed",
            "quality_score": 95,
            "email_count": 3,
            "source_url": "https://devactivo.com"
        },
        {
            "url": "https://devactivo.com/contacto",
            "domain": "devactivo.com",
            "title": "Contacto - DevActivo",
            "description": "Página de contacto de DevActivo",
            "language": "es",
            "content_type_detected": "text/html",
            "response_time": 120.3,
            "status": "processed",
            "quality_score": 85,
            "email_count": 2,
            "source_url": "https://devactivo.com"
        },
        {
            "url": "https://blog.devactivo.com/introduccion",
            "domain": "blog.devactivo.com",
            "title": "Introducción a DevActivo",
            "description": "Artículo de introducción sobre DevActivo",
            "language": "es",
            "content_type_detected": "text/html",
            "response_time": 200.1,
            "status": "processed",
            "quality_score": 90,
            "email_count": 1,
            "source_url": "https://blog.devactivo.com"
        },
        {
            "url": "https://docs.devactivo.com/api",
            "domain": "docs.devactivo.com",
            "title": "API Documentation",
            "description": "Documentación de la API de DevActivo",
            "language": "en",
            "content_type_detected": "text/html",
            "response_time": 180.7,
            "status": "processed",
            "quality_score": 92,
            "email_count": 0,
            "source_url": "https://docs.devactivo.com"
        }
    ]
    
    for website_data in websites_data:
        website = Website(**website_data)
        db.add(website)
    
    db.commit()
    
    # Obtener los IDs de los websites creados
    websites = db.query(Website).all()
    website_ids = {w.url: w.id for w in websites}
    
    # Crear emails de prueba relacionados con devactivo.com
    emails_data = [
        {
            "website_id": website_ids["https://devactivo.com"],
            "email": "contacto@devactivo.com",
            "source_page": "https://devactivo.com",
            "email_type": "business",
            "quality_score": 95,
            "is_valid": 1,
            "validation_attempts": 0,
            "domain_quality": 90
        },
        {
            "website_id": website_ids["https://devactivo.com"],
            "email": "info@devactivo.com",
            "source_page": "https://devactivo.com",
            "email_type": "business",
            "quality_score": 90,
            "is_valid": 1,
            "validation_attempts": 0,
            "domain_quality": 90
        },
        {
            "website_id": website_ids["https://devactivo.com"],
            "email": "support@devactivo.com",
            "source_page": "https://devactivo.com",
            "email_type": "business",
            "quality_score": 85,
            "is_valid": 1,
            "validation_attempts": 0,
            "domain_quality": 90
        },
        {
            "website_id": website_ids["https://devactivo.com/contacto"],
            "email": "ventas@devactivo.com",
            "source_page": "https://devactivo.com/contacto",
            "email_type": "business",
            "quality_score": 88,
            "is_valid": 1,
            "validation_attempts": 0,
            "domain_quality": 90
        },
        {
            "website_id": website_ids["https://devactivo.com/contacto"],
            "email": "comercial@devactivo.com",
            "source_page": "https://devactivo.com/contacto",
            "email_type": "business",
            "quality_score": 82,
            "is_valid": 1,
            "validation_attempts": 0,
            "domain_quality": 90
        },
        {
            "website_id": website_ids["https://blog.devactivo.com/introduccion"],
            "email": "autor@blog.devactivo.com",
            "source_page": "https://blog.devactivo.com/introduccion",
            "email_type": "personal",
            "quality_score": 75,
            "is_valid": 1,
            "validation_attempts": 0,
            "domain_quality": 80
        }
    ]
    
    for email_data in emails_data:
        email = Email(**email_data)
        db.add(email)
    
    db.commit()
    db.close()

def test_system_stats_logic():
    """Test para la lógica de estadísticas del sistema."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Simular la lógica del endpoint de estadísticas del sistema
    db = TestingSessionLocal()
    
    # Obtener estadísticas básicas
    active_jobs = db.query(ScrapingQueue).filter(
        ScrapingQueue.status.in_(["pending", "processing"])
    ).count()
    
    today = datetime.utcnow().date()
    total_jobs_today = db.query(ScrapingQueue).filter(
        ScrapingQueue.created_at >= today
    ).count()
    
    total_leads_today = db.query(Website).filter(
        Website.created_at >= today
    ).count()
    
    total_emails_today = db.query(Email).filter(
        Email.created_at >= today
    ).count()
    
    # Verificar resultados
    assert active_jobs >= 2  # Al menos los jobs processing y pending de devactivo.com
    assert total_leads_today >= 4  # Al menos los websites de devactivo.com
    assert total_emails_today >= 6  # Al menos los emails de devactivo.com
    
    db.close()

def test_scraping_stats_logic():
    """Test para la lógica de estadísticas de scraping."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Simular la lógica del endpoint de estadísticas de scraping
    db = TestingSessionLocal()
    
    # Determinar el período de tiempo (último día)
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1)
    
    # Obtener estadísticas de scraping
    total_urls_processed = db.query(Website).filter(
        Website.created_at >= start_time,
        Website.created_at <= end_time
    ).count()
    
    # Calcular tasa de éxito
    total_queue_items = db.query(ScrapingQueue).filter(
        ScrapingQueue.created_at >= start_time,
        ScrapingQueue.created_at <= end_time
    ).count()
    
    success_rate = (total_urls_processed / max(total_queue_items, 1)) * 100
    
    # Calcular tiempo promedio de procesamiento
    avg_processing_time = db.query(func.avg(Website.response_time)).filter(
        Website.created_at >= start_time,
        Website.created_at <= end_time
    ).scalar() or 0
    
    # Obtener dominios crawleados
    domains_crawled = db.query(func.count(func.distinct(Website.domain))).filter(
        Website.created_at >= start_time,
        Website.created_at <= end_time
    ).scalar() or 0
    
    # Verificar resultados
    assert total_urls_processed >= 4  # Al menos los websites de devactivo.com
    assert domains_crawled >= 3  # Al menos los dominios de devactivo.com
    assert avg_processing_time > 0  # Tiempo promedio debe ser mayor que 0
    
    db.close()

def test_job_stats_logic():
    """Test para la lógica de estadísticas de un job específico."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Simular la lógica del endpoint de estadísticas de un job
    db = TestingSessionLocal()
    
    # Verificar que el job exista
    job_id = "devactivo_job_001"
    job = db.query(ScrapingQueue).filter(ScrapingQueue.job_id == job_id).first()
    assert job is not None
    
    # Verificar resultados
    assert job.job_id == job_id
    assert job.status == "completed"
    assert job.progress == 100
    
    db.close()

def test_advanced_stats_logic():
    """Test para la lógica de estadísticas avanzadas."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Simular la lógica del endpoint de estadísticas avanzadas
    db = TestingSessionLocal()
    
    # Calcular fecha límite (últimos 30 días)
    cutoff_date = datetime.utcnow() - timedelta(days=30)
    
    # Estadísticas de sitios web
    total_websites = db.query(func.count(Website.id)).scalar()
    processed_websites = db.query(func.count(Website.id)).filter(
        Website.status == "processed"
    ).scalar()
    websites_with_emails = db.query(func.count(Website.id)).filter(
        Website.email_count > 0
    ).scalar()
    
    # Calcular puntuación promedio de calidad
    avg_quality_score = db.query(func.avg(Website.quality_score)).scalar() or 0
    
    # Estadísticas de emails
    total_emails = db.query(func.count(Email.id)).scalar()
    unique_emails = db.query(func.count(func.distinct(Email.email))).scalar()
    
    # Contar emails por tipo
    business_emails = db.query(func.count(Email.id)).filter(
        Email.email_type == "business"
    ).scalar()
    personal_emails = db.query(func.count(Email.id)).filter(
        Email.email_type == "personal"
    ).scalar()
    
    # Verificar resultados
    assert total_websites >= 4  # Al menos los websites de devactivo.com
    assert processed_websites >= 4  # Al menos los websites procesados de devactivo.com
    assert websites_with_emails >= 3  # Al menos los websites con emails de devactivo.com
    assert total_emails >= 6  # Al menos los emails de devactivo.com
    assert unique_emails >= 6  # Al menos los emails únicos de devactivo.com
    assert business_emails >= 5  # Al menos los emails business de devactivo.com
    assert personal_emails >= 1  # Al menos los emails personales de devactivo.com
    assert avg_quality_score > 0  # Puntuación promedio debe ser mayor que 0
    
    db.close()

def test_domain_stats_logic():
    """Test para la lógica de estadísticas de un dominio específico."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Simular la lógica del endpoint de estadísticas de un dominio
    db = TestingSessionLocal()
    
    # Verificar si el dominio existe
    domain = "devactivo.com"
    websites_count = db.query(func.count(Website.id)).filter(
        Website.domain == domain
    ).scalar()
    
    assert websites_count >= 2  # Al menos los websites de devactivo.com
    
    # Estadísticas del dominio
    websites_with_emails = db.query(func.count(Website.id)).filter(
        and_(
            Website.domain == domain,
            Website.email_count > 0
        )
    ).scalar()
    
    # Emails del dominio
    emails = db.query(Email).join(Website).filter(
        Website.domain == domain
    ).all()
    
    total_emails = len(emails)
    unique_emails = len(set([email.email for email in emails]))
    
    # Calcular puntuación promedio
    if emails:
        avg_quality_score = sum([email.quality_score for email in emails]) / len(emails)
    else:
        avg_quality_score = 0
    
    # Tipos de emails
    email_types = {}
    for email in emails:
        email_type = email.email_type
        if email_type in email_types:
            email_types[email_type] += 1
        else:
            email_types[email_type] = 1
    
    # Verificar resultados
    assert websites_count >= 2  # Al menos los websites de devactivo.com
    assert websites_with_emails >= 2  # Al menos los websites con emails de devactivo.com
    assert total_emails >= 3  # Al menos los emails de devactivo.com
    assert unique_emails >= 3  # Al menos los emails únicos de devactivo.com
    assert avg_quality_score > 0  # Puntuación promedio debe ser mayor que 0
    assert "business" in email_types  # Debe haber emails business
    
    db.close()