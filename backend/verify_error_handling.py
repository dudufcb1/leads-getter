"""
Script simple para verificar que el nuevo sistema de manejo de errores funciona.
"""

from app.core.exceptions_new import (
    LeadsGeneratorException,
    DatabaseException,
    ScrapingException,
    ValidationException,
    NotFoundException
)

def test_exceptions():
    """Prueba que las excepciones se puedan crear correctamente."""
    try:
        # Crear una excepción básica
        exc = LeadsGeneratorException("Error de prueba", "TEST_ERROR", {"detail": "información adicional"})
        print(f"✓ LeadsGeneratorException: {exc.message}")
        
        # Crear una excepción de base de datos
        db_exc = DatabaseException("Error de base de datos", {"query": "SELECT * FROM table"})
        print(f"✓ DatabaseException: {db_exc.message}")
        
        # Crear una excepción de scraping
        scrap_exc = ScrapingException("Error de scraping", {"url": "http://example.com"})
        print(f"✓ ScrapingException: {scrap_exc.message}")
        
        # Crear una excepción de validación
        val_exc = ValidationException("Error de validación", "campo", {"constraint": "required"})
        print(f"✓ ValidationException: {val_exc.message}")
        
        # Crear una excepción de no encontrado
        not_found_exc = NotFoundException("Recurso", "123", {"type": "job"})
        print(f"✓ NotFoundException: {not_found_exc.message}")
        
        print("\n✅ Todas las excepciones se crearon correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear excepciones: {e}")
        return False

if __name__ == "__main__":
    test_exceptions()