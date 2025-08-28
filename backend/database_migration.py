#!/usr/bin/env python3
"""
Script para migrar la base de datos y agregar los nuevos campos necesarios.
"""

import sqlite3
import os
import uuid
from pathlib import Path

def migrate_database():
    """Migra la base de datos para agregar los nuevos campos."""
    # Determinar la ruta de la base de datos
    db_path = Path(__file__).parent / "leads_generator.db"
    
    if not db_path.exists():
        print("❌ Base de datos no encontrada. Asegúrate de que el backend se haya ejecutado al menos una vez.")
        return False
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar si los campos ya existen
        cursor.execute("PRAGMA table_info(scraping_queue)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Si no existe job_id, necesitamos recrear la tabla
        if 'job_id' not in columns:
            print("➕ Agregando campo 'job_id' y reestructurando tabla...")
            
            # Eliminar tabla nueva si existe
            cursor.execute("DROP TABLE IF EXISTS scraping_queue_new")
            
            # Crear nueva tabla con la estructura actualizada
            cursor.execute("""
                CREATE TABLE scraping_queue_new (
                    id INTEGER PRIMARY KEY,
                    job_id TEXT UNIQUE,
                    url TEXT NOT NULL,
                    priority INTEGER DEFAULT 0,
                    depth_level INTEGER DEFAULT 0,
                    status TEXT DEFAULT 'pending',
                    attempts INTEGER DEFAULT 0,
                    progress INTEGER DEFAULT 0,
                    total_items INTEGER DEFAULT 0,
                    processed_items INTEGER DEFAULT 0,
                    created_at DATETIME,
                    updated_at DATETIME
                )
            """)
            
            # Copiar datos de la tabla antigua a la nueva
            cursor.execute("""
                INSERT INTO scraping_queue_new
                (id, url, priority, depth_level, status, attempts, progress, total_items, processed_items, created_at, updated_at)
                SELECT id, url, priority, depth_level, status, attempts,
                       COALESCE(progress, 0), COALESCE(total_items, 0), COALESCE(processed_items, 0),
                       created_at, updated_at
                FROM scraping_queue
            """)
            
            # Generar job_id para los registros existentes (usando parte del hash de la URL)
            cursor.execute("SELECT id, url FROM scraping_queue_new WHERE job_id IS NULL")
            rows = cursor.fetchall()
            for row in rows:
                job_id = str(uuid.uuid4())[:8]  # ID corto único
                cursor.execute("UPDATE scraping_queue_new SET job_id = ? WHERE id = ?", (job_id, row[0]))
            
            # Eliminar tabla antigua y renombrar la nueva
            cursor.execute("DROP TABLE scraping_queue")
            cursor.execute("ALTER TABLE scraping_queue_new RENAME TO scraping_queue")
            
            # Crear índices
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_scraping_queue_job_id ON scraping_queue(job_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_scraping_queue_url ON scraping_queue(url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_scraping_queue_priority ON scraping_queue(priority)")
        else:
            # Agregar campos que no existen
            if 'progress' not in columns:
                print("➕ Agregando campo 'progress'...")
                cursor.execute("ALTER TABLE scraping_queue ADD COLUMN progress INTEGER DEFAULT 0")
            
            if 'total_items' not in columns:
                print("➕ Agregando campo 'total_items'...")
                cursor.execute("ALTER TABLE scraping_queue ADD COLUMN total_items INTEGER DEFAULT 0")
            
            if 'processed_items' not in columns:
                print("➕ Agregando campo 'processed_items'...")
                cursor.execute("ALTER TABLE scraping_queue ADD COLUMN processed_items INTEGER DEFAULT 0")
        
        # Verificar y agregar nuevos estados al enum
        # En SQLite, los enums no se verifican, pero en SQLAlchemy sí
        # La migración de enums se maneja en el modelo
        
        # Confirmar cambios
        conn.commit()
        conn.close()
        
        print("✅ Migración completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Iniciando migración de base de datos...")
    migrate_database()