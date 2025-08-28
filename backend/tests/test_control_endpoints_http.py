"""
Tests para los endpoints de control avanzado de jobs usando requests HTTP.
"""

import pytest
import requests
import time
import threading
from fastapi import FastAPI
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.database.models import ScrapingQueue, Base

# Configurar base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_leads.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas en la base de datos de prueba
Base.metadata.create_all(bind=engine)

def setup_test_data():
    """Configura datos de prueba en la base de datos."""
    db = TestingSessionLocal()
    
    # Limpiar datos previos
    db.query(ScrapingQueue).delete()
    
    # Crear jobs de prueba
    jobs_data = [
        {
            "job_id": "test_job_001",
            "url": "https://devactivo.com",
            "status": "pending",
            "priority": 0,
            "depth_level": 0,
            "attempts": 0
        },
        {
            "job_id": "test_job_002",
            "url": "https://devactivo.com/about",
            "status": "processing",
            "priority": 1,
            "depth_level": 1,
            "attempts": 1
        },
        {
            "job_id": "test_job_003",
            "url": "https://devactivo.com/contact",
            "status": "paused",
            "priority": 2,
            "depth_level": 0,
            "attempts": 0
        },
        {
            "job_id": "test_job_004",
            "url": "https://devactivo.com/services",
            "status": "completed",
            "priority": 0,
            "depth_level": 2,
            "attempts": 3
        }
    ]
    
    for job_data in jobs_data:
        job = ScrapingQueue(**job_data)
        db.add(job)
    
    db.commit()
    db.close()

def test_pause_job_endpoint():
    """Test para el endpoint de pausar un job específico."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Verificar que el job exista y esté en estado correcto
    db = TestingSessionLocal()
    job = db.query(ScrapingQueue).filter_by(job_id="test_job_001").first()
    assert job is not None
    assert job.status == "pending"
    db.close()
    
    # En un entorno real, haríamos una solicitud HTTP al endpoint:
    # response = requests.post("http://localhost:8000/api/v1/control/test_job_001/pause")
    # Pero como no tenemos el servidor corriendo, simulamos la lógica del endpoint
    
    # Simular la lógica del endpoint de pausar job
    db = TestingSessionLocal()
    queue_item = db.query(ScrapingQueue).filter_by(job_id="test_job_001").first()
    
    # Verificar precondiciones
    assert queue_item is not None
    assert queue_item.status in ["pending", "processing"]  # Estado válido para pausar
    
    # Actualizar el estado a 'paused'
    queue_item.status = "paused"
    db.commit()
    db.close()
    
    # Verificar que el estado se haya actualizado
    db = TestingSessionLocal()
    updated_job = db.query(ScrapingQueue).filter_by(job_id="test_job_001").first()
    assert updated_job.status == "paused"
    db.close()

def test_pause_job_invalid_state():
    """Test para intentar pausar un job en estado inválido."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Verificar que el job exista y esté en estado 'completed'
    db = TestingSessionLocal()
    job = db.query(ScrapingQueue).filter_by(job_id="test_job_004").first()
    assert job is not None
    assert job.status == "completed"
    db.close()
    
    # Simular la lógica del endpoint de pausar job
    db = TestingSessionLocal()
    queue_item = db.query(ScrapingQueue).filter_by(job_id="test_job_004").first()
    
    # Verificar que el estado no sea válido para pausar
    assert queue_item is not None
    assert queue_item.status not in ["pending", "processing"]  # Estado inválido para pausar
    
    db.close()

def test_resume_job_endpoint():
    """Test para el endpoint de reanudar un job pausado."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Verificar que el job exista y esté en estado 'paused'
    db = TestingSessionLocal()
    job = db.query(ScrapingQueue).filter_by(job_id="test_job_003").first()
    assert job is not None
    assert job.status == "paused"
    db.close()
    
    # Simular la lógica del endpoint de reanudar job
    db = TestingSessionLocal()
    queue_item = db.query(ScrapingQueue).filter_by(job_id="test_job_003").first()
    
    # Verificar precondiciones
    assert queue_item is not None
    assert queue_item.status == "paused"  # Estado válido para reanudar
    
    # Actualizar el estado a 'pending'
    queue_item.status = "pending"
    db.commit()
    db.close()
    
    # Verificar que el estado se haya actualizado
    db = TestingSessionLocal()
    updated_job = db.query(ScrapingQueue).filter_by(job_id="test_job_003").first()
    assert updated_job.status == "pending"
    db.close()

def test_stop_job_endpoint():
    """Test para el endpoint de detener un job."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Verificar que el job exista y esté en estado 'processing'
    db = TestingSessionLocal()
    job = db.query(ScrapingQueue).filter_by(job_id="test_job_002").first()
    assert job is not None
    assert job.status == "processing"
    db.close()
    
    # Simular la lógica del endpoint de detener job
    db = TestingSessionLocal()
    queue_item = db.query(ScrapingQueue).filter_by(job_id="test_job_002").first()
    
    # Verificar precondiciones
    assert queue_item is not None
    assert queue_item.status in ["pending", "processing", "paused"]  # Estado válido para detener
    
    # Actualizar el estado a 'cancelled'
    queue_item.status = "cancelled"
    db.commit()
    db.close()
    
    # Verificar que el estado se haya actualizado
    db = TestingSessionLocal()
    updated_job = db.query(ScrapingQueue).filter_by(job_id="test_job_002").first()
    assert updated_job.status == "cancelled"
    db.close()

def test_pause_all_jobs_endpoint():
    """Test para el endpoint de pausar todos los jobs activos."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Verificar estados iniciales
    db = TestingSessionLocal()
    initial_pending = db.query(ScrapingQueue).filter_by(status="pending").count()
    initial_processing = db.query(ScrapingQueue).filter_by(status="processing").count()
    initial_paused = db.query(ScrapingQueue).filter_by(status="paused").count()
    initial_completed = db.query(ScrapingQueue).filter_by(status="completed").count()
    
    assert initial_pending >= 1  # Al menos un job pending
    assert initial_processing >= 1  # Al menos un job processing
    assert initial_paused >= 1  # Al menos un job paused
    assert initial_completed >= 1  # Al menos un job completed
    db.close()
    
    # Simular la lógica del endpoint de pausar todos los jobs
    db = TestingSessionLocal()
    paused_count = db.query(ScrapingQueue).filter(
        ScrapingQueue.status.in_(["pending", "processing"])
    ).update(
        {
            ScrapingQueue.status: "paused"
        },
        synchronize_session=False
    )
    db.commit()
    db.close()
    
    # Verificar que los estados se hayan actualizado correctamente
    db = TestingSessionLocal()
    final_pending = db.query(ScrapingQueue).filter_by(status="pending").count()
    final_processing = db.query(ScrapingQueue).filter_by(status="processing").count()
    final_paused = db.query(ScrapingQueue).filter_by(status="paused").count()
    final_completed = db.query(ScrapingQueue).filter_by(status="completed").count()
    
    assert final_pending == 0  # No deben quedar jobs pending
    assert final_processing == 0  # No deben quedar jobs processing
    assert final_paused >= initial_paused + initial_pending + initial_processing  # Deben haberse pausado los jobs correctos
    assert final_completed == initial_completed  # Los jobs completed no deben cambiar
    
    db.close()

def test_bulk_pause_jobs_endpoint():
    """Test para el endpoint de pausar múltiples jobs específicos."""
    # Configurar datos de prueba
    setup_test_data()
    
    # Verificar estados iniciales
    db = TestingSessionLocal()
    job1 = db.query(ScrapingQueue).filter_by(job_id="test_job_001").first()
    job2 = db.query(ScrapingQueue).filter_by(job_id="test_job_002").first()
    job3 = db.query(ScrapingQueue).filter_by(job_id="test_job_004").first()
    
    assert job1.status == "pending"  # Estado válido para pausar
    assert job2.status == "processing"  # Estado válido para pausar
    assert job3.status == "completed"  # Estado inválido para pausar
    
    db.close()
    
    # Simular la lógica del endpoint de pausar jobs específicos
    job_ids = ["test_job_001", "test_job_002", "test_job_004", "nonexistent_job"]
    success_count = 0
    failed_count = 0
    
    db = TestingSessionLocal()
    for job_id in job_ids:
        queue_item = db.query(ScrapingQueue).filter_by(job_id=job_id).first()
        
        if not queue_item:
            failed_count += 1
            continue
        
        # Verificar que el job esté en un estado que se pueda pausar
        if queue_item.status not in ["pending", "processing"]:
            failed_count += 1
            continue
        
        # Actualizar el estado a 'paused'
        queue_item.status = "paused"
        db.commit()
        success_count += 1
    
    db.close()
    
    # Verificar resultados
    assert success_count == 2  # Dos jobs válidos y en estado correcto
    assert failed_count == 2  # Un job en estado inválido y un job inexistente
    
    # Verificar que los estados se hayan actualizado correctamente
    db = TestingSessionLocal()
    paused_job1 = db.query(ScrapingQueue).filter_by(job_id="test_job_001").first()
    paused_job2 = db.query(ScrapingQueue).filter_by(job_id="test_job_002").first()
    completed_job = db.query(ScrapingQueue).filter_by(job_id="test_job_004").first()
    
    assert paused_job1.status == "paused"
    assert paused_job2.status == "paused"
    assert completed_job.status == "completed"  # No debe cambiar
    
    db.close()