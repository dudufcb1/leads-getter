"""
Tests para los endpoints de estadísticas usando devactivo.com como ejemplo.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import sys
import os

# Añadir el directorio backend al path para resolver importaciones
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.database.models import ScrapingQueue, Website, Email, Base
from app.database.database import get_db

# Configurar base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_leads.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas en la base de datos de prueba
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override de la dependencia de base de datos para pruebas."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Aplicar override a la aplicación
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

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
            "progress": 100.0
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
            "progress": 50.0
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
            "progress": 0.0
        }
    ]
    
    for job_data in jobs_data:
        job = ScrapingQueue(**job_data)
        db.add(job)
    
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
            "quality_score": 0.95,
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
            "quality_score": 0.85,
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
            "quality_score": 0.90,
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
            "quality_score": 0.92,
            "email_count": 0,
            "source_url": "https://docs.devactivo.com"
        }
    ]
    
    for website_data in websites_data:
        website = Website(**website_data)
        db.add(website)
    
    # Crear emails de prueba relacionados con devactivo.com
    emails_data = [
        {
            "email": "contacto@devactivo.com",
            "email_type": "business",
            "quality_score": 0.95,
            "is_valid": True,
            "website_id": 1  # Relacionado con el primer website
        },
        {
            "email": "info@devactivo.com",
            "email_type": "business",
            "quality_score": 0.90,
            "is_valid": True,
            "website_id": 1  # Relacionado con el primer website
        },
        {
            "email": "support@devactivo.com",
            "email_type": "business",
            "quality_score": 0.85,
            "is_valid": True,
            "website_id": 1  # Relacionado con el primer website
        },
        {
            "email": "ventas@devactivo.com",
            "email_type": "business",
            "quality_score": 0.88,
            "is_valid": True,
            "website_id": 2  # Relacionado con el segundo website
        },
        {
            "email": "comercial@devactivo.com",
            "email_type": "business",
            "quality_score": 0.82,
            "is_valid": True,
            "website_id": 2  # Relacionado con el segundo website
        },
        {
            "email": "autor@blog.devactivo.com",
            "email_type": "personal",
            "quality_score": 0.75,
            "is_valid": True,
            "website_id": 3  # Relacionado con el tercer website
        }
    ]
    
    for email_data in emails_data:
        email = Email(**email_data)
        db.add(email)
    
    db.commit()
    db.close()

def test_system_stats_endpoint():
    """Test para el endpoint de estadísticas del sistema."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Hacer solicitud al endpoint
    response = client.get("/api/v1/stats/system")
    
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    data = response.json()
    
    # Verificar campos requeridos en la respuesta
    assert "active_jobs" in data
    assert "total_jobs_today" in data
    assert "total_leads_today" in data
    assert "total_emails_today" in data
    assert "system_health" in data
    assert "recent_activity" in data
    assert "performance_summary" in data
    
    # Verificar valores específicos relacionados con devactivo.com
    assert data["active_jobs"] >= 2  # Al menos los jobs processing y pending de devactivo.com
    assert data["total_leads_today"] >= 4  # Al menos los websites de devactivo.com
    assert data["total_emails_today"] >= 6  # Al menos los emails de devactivo.com

def test_scraping_stats_endpoint():
    """Test para el endpoint de estadísticas de scraping."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Hacer solicitud al endpoint
    response = client.get("/api/v1/stats/scraping?period=day")
    
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    data = response.json()
    
    # Verificar campos requeridos en la respuesta
    assert "period" in data
    assert "total_urls_processed" in data
    assert "success_rate" in data
    assert "avg_processing_time" in data
    assert "domains_crawled" in data
    assert "duplicates_filtered" in data
    assert "urls_by_hour" in data
    assert "top_domains" in data
    
    # Verificar valores específicos relacionados con devactivo.com
    assert data["total_urls_processed"] >= 4  # Al menos los websites de devactivo.com
    assert data["domains_crawled"] >= 3  # Al menos los dominios de devactivo.com
    assert len(data["top_domains"]) >= 3  # Al menos los dominios de devactivo.com

def test_job_stats_endpoint():
    """Test para el endpoint de estadísticas de un job específico."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Hacer solicitud al endpoint para un job de devactivo.com
    response = client.get("/api/v1/stats/jobs/devactivo_job_001")
    
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    data = response.json()
    
    # Verificar campos requeridos en la respuesta
    assert "job_id" in data
    assert "duration" in data
    assert "efficiency" in data
    assert "status_distribution" in data
    assert "performance_history" in data
    
    # Verificar valores específicos del job de devactivo.com
    assert data["job_id"] == "devactivo_job_001"

def test_historical_stats_endpoint():
    """Test para el endpoint de estadísticas históricas."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Hacer solicitud al endpoint
    response = client.get("/api/v1/stats/historical?period=week")
    
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    data = response.json()
    
    # Verificar campos requeridos en la respuesta
    assert "period" in data
    assert "data" in data
    
    # Verificar que se obtengan datos históricos
    assert isinstance(data["data"], list)

def test_performance_stats_endpoint():
    """Test para el endpoint de métricas de rendimiento."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Hacer solicitud al endpoint
    response = client.get("/api/v1/stats/performance")
    
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    data = response.json()
    
    # Verificar campos requeridos en la respuesta
    assert "scraping_performance" in data
    assert "system_resources" in data
    assert "database_performance" in data
    assert "queue_status" in data

def test_sources_stats_endpoint():
    """Test para el endpoint de estadísticas por fuente."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Hacer solicitud al endpoint
    response = client.get("/api/v1/stats/sources")
    
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    data = response.json()
    
    # Verificar campos requeridos en la respuesta
    assert "sources" in data
    assert "top_sources" in data
    
    # Verificar que se obtengan fuentes relacionadas con devactivo.com
    assert len(data["sources"]) >= 3  # Al menos los dominios de devactivo.com
    assert len(data["top_sources"]) >= 3  # Al menos los dominios de devactivo.com

def test_advanced_stats_endpoint():
    """Test para el endpoint de estadísticas avanzadas."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Hacer solicitud al endpoint
    response = client.get("/api/v1/advanced-stats/advanced?days=30")
    
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    data = response.json()
    
    # Verificar campos requeridos en la respuesta
    assert "websites" in data
    assert "emails" in data
    assert "jobs" in data
    assert "languages" in data
    assert "content_types" in data
    assert "top_domains" in data
    assert "scraping_trends" in data
    
    # Verificar valores específicos relacionados con devactivo.com
    websites_stats = data["websites"]
    assert websites_stats["total_websites"] >= 4  # Al menos los websites de devactivo.com
    
    emails_stats = data["emails"]
    assert emails_stats["total_emails"] >= 6  # Al menos los emails de devactivo.com
    assert emails_stats["unique_emails"] >= 6  # Al menos los emails únicos de devactivo.com
    
    jobs_stats = data["jobs"]
    assert jobs_stats["total_jobs"] >= 3  # Al menos los jobs de devactivo.com

def test_realtime_stats_endpoint():
    """Test para el endpoint de estadísticas en tiempo real."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Hacer solicitud al endpoint
    response = client.get("/api/v1/advanced-stats/realtime")
    
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    data = response.json()
    
    # Verificar campos requeridos en la respuesta
    assert "active_sessions" in data
    assert "processing_jobs" in data
    assert "emails_found_last_hour" in data
    assert "websites_processed_last_hour" in data
    assert "system_load" in data
    assert "memory_usage" in data
    assert "cpu_usage" in data

def test_domain_stats_endpoint():
    """Test para el endpoint de estadísticas de un dominio específico."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Hacer solicitud al endpoint para el dominio de devactivo.com
    response = client.get("/api/v1/advanced-stats/domain/devactivo.com")
    
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    data = response.json()
    
    # Verificar campos requeridos en la respuesta
    assert "domain" in data
    assert "total_websites" in data
    assert "websites_with_emails" in data
    assert "total_emails" in data
    assert "unique_emails" in data
    assert "average_quality_score" in data
    assert "email_types" in data
    
    # Verificar valores específicos del dominio devactivo.com
    assert data["domain"] == "devactivo.com"
    assert data["total_websites"] >= 2  # Al menos los websites de devactivo.com
    assert data["total_emails"] >= 3  # Al menos los emails de devactivo.com
    assert data["unique_emails"] >= 3  # Al menos los emails únicos de devactivo.com

def test_detailed_job_stats_endpoint():
    """Test para el endpoint de estadísticas detalladas de un job."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Hacer solicitud al endpoint para un job de devactivo.com
    response = client.get("/api/v1/advanced-stats/job/devactivo_job_001/detailed")
    
    # Verificar que la respuesta sea exitosa
    assert response.status_code == 200
    data = response.json()
    
    # Verificar campos requeridos en la respuesta
    assert "job_id" in data
    assert "status" in data
    assert "progress" in data
    assert "total_items" in data
    assert "processed_items" in data
    assert "attempts" in data
    assert "log_summary" in data
    assert "recent_logs" in data
    
    # Verificar valores específicos del job de devactivo.com
    assert data["job_id"] == "devactivo_job_001"
    assert data["status"] == "completed"
    assert data["progress"] == 100.0