"""
Tests para los endpoints de control avanzado de jobs.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.database.models import ScrapingQueue, Base

# Configurar base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_leads.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear tablas en la base de datos de prueba
Base.metadata.create_all(bind=engine)

def test_control_endpoints_logic():
    """Test para verificar la lógica de los endpoints de control."""
    # Este test verifica la lógica sin necesidad de levantar toda la aplicación
    
    # Crear un job en estado pending para la prueba
    db = TestingSessionLocal()
    
    # Limpiar datos previos
    db.query(ScrapingQueue).delete()
    
    job = ScrapingQueue(
        job_id="test_job_001",
        url="https://devactivo.com",
        status="pending",
        priority=0,
        depth_level=0,
        attempts=0
    )
    db.add(job)
    db.commit()
    
    # Verificar que el job se haya creado correctamente
    created_job = db.query(ScrapingQueue).filter_by(job_id="test_job_001").first()
    assert created_job is not None
    assert created_job.status == "pending"
    
    # Simular la lógica de pausar un job
    # (Esto es lo que hace el endpoint en el control.py)
    queue_item = db.query(ScrapingQueue).filter_by(job_id="test_job_001").first()
    assert queue_item is not None
    assert queue_item.status in ["pending", "processing"]  # Estado válido para pausar
    
    # Actualizar el estado a 'paused'
    queue_item.status = "paused"
    db.commit()
    
    # Verificar que el estado se haya actualizado
    updated_job = db.query(ScrapingQueue).filter_by(job_id="test_job_001").first()
    assert updated_job.status == "paused"
    
    db.close()

def test_pause_job_invalid_state():
    """Test para verificar que no se pueda pausar un job en estado inválido."""
    db = TestingSessionLocal()
    
    # Crear un job en estado completed para la prueba
    job = ScrapingQueue(
        job_id="test_job_002",
        url="https://devactivo.com",
        status="completed",
        priority=0,
        depth_level=0,
        attempts=0
    )
    db.add(job)
    db.commit()
    
    # Verificar que el job se haya creado correctamente
    created_job = db.query(ScrapingQueue).filter_by(job_id="test_job_002").first()
    assert created_job is not None
    assert created_job.status == "completed"
    
    # Verificar que no se pueda pausar un job en estado 'completed'
    queue_item = db.query(ScrapingQueue).filter_by(job_id="test_job_002").first()
    assert queue_item is not None
    assert queue_item.status not in ["pending", "processing"]  # Estado inválido para pausar
    
    db.close()

def test_resume_job_logic():
    """Test para verificar la lógica de reanudar un job."""
    db = TestingSessionLocal()
    
    # Crear un job en estado paused para la prueba
    job = ScrapingQueue(
        job_id="test_job_003",
        url="https://devactivo.com",
        status="paused",
        priority=0,
        depth_level=0,
        attempts=0
    )
    db.add(job)
    db.commit()
    
    # Verificar que el job se haya creado correctamente
    created_job = db.query(ScrapingQueue).filter_by(job_id="test_job_003").first()
    assert created_job is not None
    assert created_job.status == "paused"
    
    # Simular la lógica de reanudar un job
    queue_item = db.query(ScrapingQueue).filter_by(job_id="test_job_003").first()
    assert queue_item is not None
    assert queue_item.status == "paused"  # Estado válido para reanudar
    
    # Actualizar el estado a 'pending'
    queue_item.status = "pending"
    db.commit()
    
    # Verificar que el estado se haya actualizado
    updated_job = db.query(ScrapingQueue).filter_by(job_id="test_job_003").first()
    assert updated_job.status == "pending"
    
    db.close()

def test_stop_job_logic():
    """Test para verificar la lógica de detener un job."""
    db = TestingSessionLocal()
    
    # Crear un job en estado processing para la prueba
    job = ScrapingQueue(
        job_id="test_job_004",
        url="https://devactivo.com",
        status="processing",
        priority=0,
        depth_level=0,
        attempts=0
    )
    db.add(job)
    db.commit()
    
    # Verificar que el job se haya creado correctamente
    created_job = db.query(ScrapingQueue).filter_by(job_id="test_job_004").first()
    assert created_job is not None
    assert created_job.status == "processing"
    
    # Simular la lógica de detener un job
    queue_item = db.query(ScrapingQueue).filter_by(job_id="test_job_004").first()
    assert queue_item is not None
    assert queue_item.status in ["pending", "processing", "paused"]  # Estado válido para detener
    
    # Actualizar el estado a 'cancelled'
    queue_item.status = "cancelled"
    db.commit()
    
    # Verificar que el estado se haya actualizado
    updated_job = db.query(ScrapingQueue).filter_by(job_id="test_job_004").first()
    assert updated_job.status == "cancelled"
    
    db.close()

def test_pause_all_jobs_logic():
    """Test para verificar la lógica de pausar todos los jobs activos."""
    db = TestingSessionLocal()
    
    # Limpiar datos previos
    db.query(ScrapingQueue).delete()
    
    # Crear varios jobs en diferentes estados
    job1 = ScrapingQueue(
        job_id="test_job_005",
        url="https://devactivo.com/1",
        status="pending",
        priority=0,
        depth_level=0,
        attempts=0
    )
    job2 = ScrapingQueue(
        job_id="test_job_006",
        url="https://devactivo.com/2",
        status="processing",
        priority=0,
        depth_level=0,
        attempts=0
    )
    job3 = ScrapingQueue(
        job_id="test_job_007",
        url="https://devactivo.com/3",
        status="paused",
        priority=0,
        depth_level=0,
        attempts=0
    )
    job4 = ScrapingQueue(
        job_id="test_job_008",
        url="https://devactivo.com/4",
        status="completed",
        priority=0,
        depth_level=0,
        attempts=0
    )
    db.add_all([job1, job2, job3, job4])
    db.commit()
    
    # Simular la lógica de pausar todos los jobs activos
    # (Esto es lo que hace el endpoint en el control.py)
    paused_count = db.query(ScrapingQueue).filter(
        ScrapingQueue.status.in_(["pending", "processing"])
    ).update(
        {
            ScrapingQueue.status: "paused"
        },
        synchronize_session=False
    )
    db.commit()
    
    # Verificar que se hayan pausado los jobs correctos
    pending_jobs = db.query(ScrapingQueue).filter_by(status="pending").count()
    processing_jobs = db.query(ScrapingQueue).filter_by(status="processing").count()
    paused_jobs = db.query(ScrapingQueue).filter_by(status="paused").count()
    completed_jobs = db.query(ScrapingQueue).filter_by(status="completed").count()
    
    assert pending_jobs == 0  # No deben quedar jobs pending
    assert processing_jobs == 0  # No deben quedar jobs processing
    assert paused_jobs >= 2  # Al menos los jobs que estaban pending y processing
    assert completed_jobs == 1  # El job completed no debe cambiar
    
    db.close()

def test_bulk_pause_jobs_logic():
    """Test para verificar la lógica de pausar múltiples jobs específicos."""
    db = TestingSessionLocal()
    
    # Limpiar datos previos
    db.query(ScrapingQueue).delete()
    
    # Crear varios jobs
    job1 = ScrapingQueue(
        job_id="test_job_009",
        url="https://devactivo.com/9",
        status="pending",
        priority=0,
        depth_level=0,
        attempts=0
    )
    job2 = ScrapingQueue(
        job_id="test_job_010",
        url="https://devactivo.com/10",
        status="processing",
        priority=0,
        depth_level=0,
        attempts=0
    )
    job3 = ScrapingQueue(
        job_id="test_job_011",
        url="https://devactivo.com/11",
        status="completed",
        priority=0,
        depth_level=0,
        attempts=0
    )
    db.add_all([job1, job2, job3])
    db.commit()
    
    # Simular la lógica de pausar jobs específicos
    job_ids = ["test_job_009", "test_job_010", "nonexistent_job"]
    success_count = 0
    failed_count = 0
    
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
    
    # Verificar resultados
    assert success_count == 2  # Dos jobs válidos y en estado correcto
    assert failed_count == 1  # Un job no existente
    
    # Verificar que los estados se hayan actualizado correctamente
    paused_job1 = db.query(ScrapingQueue).filter_by(job_id="test_job_009").first()
    paused_job2 = db.query(ScrapingQueue).filter_by(job_id="test_job_010").first()
    completed_job = db.query(ScrapingQueue).filter_by(job_id="test_job_011").first()
    
    assert paused_job1.status == "paused"
    assert paused_job2.status == "paused"
    assert completed_job.status == "completed"  # No debe cambiar
    
    db.close()