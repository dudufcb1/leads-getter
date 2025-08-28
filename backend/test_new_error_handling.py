"""
Script para probar el nuevo sistema de manejo de errores.
"""

import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database.database import Base, get_db
from app.database.models import ScrapingQueue

# Configurar base de datos de prueba
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_leads_generator.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Override para la dependencia de base de datos en pruebas."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Aplicar override
app.dependency_overrides[get_db] = override_get_db

# Crear cliente de prueba
client = TestClient(app)

class TestNewErrorHandling(unittest.TestCase):
    """Pruebas para el nuevo sistema de manejo de errores."""
    
    @classmethod
    def setUpClass(cls):
        """Configuración inicial antes de todas las pruebas."""
        # Crear tablas
        Base.metadata.create_all(bind=engine)
    
    @classmethod
    def tearDownClass(cls):
        """Limpieza final después de todas las pruebas."""
        # Eliminar tablas
        Base.metadata.drop_all(bind=engine)
    
    def setUp(self):
        """Configuración antes de cada prueba."""
        # Limpiar base de datos
        db = TestingSessionLocal()
        db.query(ScrapingQueue).delete()
        db.commit()
        db.close()
    
    def test_create_job_with_empty_url(self):
        """Prueba crear trabajo con URL vacía."""
        response = client.post("/api/v1/jobs/", json={
            "start_url": "",
            "depth": 3,
            "languages": ["es", "en"],
            "delay": 2.0
        })
        
        # Verificar que se devuelve un error de validación con el nuevo formato
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["type"], "VALIDATION_ERROR")
        self.assertIn("vacía", data["error"]["message"])
    
    def test_create_job_with_invalid_url(self):
        """Prueba crear trabajo con URL inválida."""
        response = client.post("/api/v1/jobs/", json={
            "start_url": "invalid-url",
            "depth": 3,
            "languages": ["es", "en"],
            "delay": 2.0
        })
        
        # Verificar que se devuelve un error de validación con el nuevo formato
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["type"], "VALIDATION_ERROR")
        self.assertIn("http://", data["error"]["message"])
    
    def test_get_job_status_with_empty_url(self):
        """Prueba obtener estado de trabajo con URL vacía."""
        response = client.get("/api/v1/jobs/status?job_url=")
        
        # Verificar que se devuelve un error de validación con el nuevo formato
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["type"], "VALIDATION_ERROR")
        self.assertIn("vacía", data["error"]["message"])
    
    def test_get_job_status_with_nonexistent_job(self):
        """Prueba obtener estado de trabajo inexistente."""
        response = client.get("/api/v1/jobs/status?job_url=https://nonexistent.com")
        
        # Verificar que se devuelve un error de no encontrado con el nuevo formato
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["type"], "NOT_FOUND")
        self.assertIn("no encontrado", data["error"]["message"])
    
    def test_get_leads_with_invalid_page(self):
        """Prueba obtener leads con número de página inválido."""
        response = client.get("/api/v1/leads?page=0&limit=50")
        
        # Verificar que se devuelve un error de validación con el nuevo formato
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["type"], "VALIDATION_ERROR")
        self.assertIn("mayor o igual a 1", data["error"]["message"])
    
    def test_get_leads_with_invalid_limit(self):
        """Prueba obtener leads con límite inválido."""
        response = client.get("/api/v1/leads?page=1&limit=150")
        
        # Verificar que se devuelve un error de validación con el nuevo formato
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertIn("error", data)
        self.assertEqual(data["error"]["type"], "VALIDATION_ERROR")
        self.assertIn("entre 1 y 100", data["error"]["message"])

if __name__ == "__main__":
    unittest.main()