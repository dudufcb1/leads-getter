#!/usr/bin/env python3
"""
Script para inicializar la base de datos de prueba.
"""

import sqlite3
import os

def init_database():
    """Inicializa la base de datos de prueba."""
    # Crear conexión a la base de datos
    conn = sqlite3.connect('app_database.db')
    cursor = conn.cursor()
    
    # Crear tabla de websites
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS websites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            domain TEXT NOT NULL,
            response_time INTEGER,
            quality_score REAL,
            is_spam INTEGER DEFAULT 0,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear tabla de emails
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            website_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (website_id) REFERENCES websites (id)
        )
    ''')
    
    # Crear tabla de scraping_queue
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scraping_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE NOT NULL,
            status TEXT NOT NULL,
            processed_items INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            updated_at TIMESTAMP
        )
    ''')
    
    # Crear tabla de scraping_logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scraping_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            url TEXT,
            job_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear tabla de system_stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP NOT NULL,
            cpu_usage REAL,
            memory_usage INTEGER,  -- en MB
            disk_usage INTEGER,    -- en GB
            active_connections INTEGER
        )
    ''')
    
    # Crear tabla de scraping_stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scraping_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP NOT NULL,
            urls_processed INTEGER,
            success_rate REAL,
            avg_response_time INTEGER,
            errors_count INTEGER
        )
    ''')
    
    # Crear tabla de job_stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT UNIQUE NOT NULL,
            duration INTEGER,  -- en segundos
            efficiency REAL,
            performance_history TEXT  -- JSON
        )
    ''')
    
    # Guardar cambios y cerrar conexión
    conn.commit()
    conn.close()
    
    print("✅ Base de datos inicializada exitosamente")

def main():
    """Función principal."""
    print("🚀 Inicializando base de datos de prueba...")
    print("=" * 50)
    
    try:
        init_database()
        print("\n🎉 ¡Base de datos inicializada exitosamente!")
        print("\nAhora puedes generar datos de prueba.")
        return 0
    except Exception as e:
        print(f"\n❌ Error al inicializar la base de datos: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)