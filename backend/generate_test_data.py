#!/usr/bin/env python3
"""
Script para generar datos de prueba para el sistema de estadísticas.
"""

import sqlite3
import random
from datetime import datetime, timedelta
import json

def generate_test_data():
    """Genera datos de prueba para el sistema de estadísticas."""
    # Conectar a la base de datos
    conn = sqlite3.connect('app_database.db')
    cursor = conn.cursor()
    
    # Generar datos de websites
    print("Generando datos de websites...")
    websites_data = []
    for i in range(200):
        created_at = datetime.utcnow() - timedelta(hours=random.randint(0, 168))  # Última semana
        domain = f"devactivo.com"
        url = f"https://{domain}/page{i}"
        response_time = random.randint(50, 500)
        quality_score = round(random.uniform(5.0, 10.0), 2)
        is_spam = random.choice([0, 1])
        
        websites_data.append((
            url, domain, response_time, quality_score, is_spam, created_at
        ))
    
    cursor.executemany('''
        INSERT OR IGNORE INTO websites (url, domain, response_time, quality_score, is_spam, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', websites_data)
    
    # Generar datos de emails
    print("Generando datos de emails...")
    emails_data = []
    for i in range(100):
        created_at = datetime.utcnow() - timedelta(hours=random.randint(0, 168))  # Última semana
        email = f"user{i}@devactivo.com"
        website_id = random.randint(1, 200)
        
        emails_data.append((
            email, website_id, created_at
        ))
    
    cursor.executemany('''
        INSERT OR IGNORE INTO emails (email, website_id, created_at)
        VALUES (?, ?, ?)
    ''', emails_data)
    
    # Generar datos de scraping queue
    print("Generando datos de scraping queue...")
    queue_data = []
    statuses = ["pending", "processing", "completed", "failed", "paused", "cancelled"]
    
    for i in range(50):
        created_at = datetime.utcnow() - timedelta(hours=random.randint(0, 168))  # Última semana
        started_at = created_at + timedelta(minutes=random.randint(0, 30)) if random.choice([True, False]) else None
        updated_at = created_at + timedelta(hours=random.randint(1, 24)) if random.choice([True, False]) else None
        processed_items = random.randint(0, 100) if random.choice([True, False]) else 0
        status = random.choice(statuses)
        job_id = f"job_{random.randint(1000, 9999)}"
        
        queue_data.append((
            job_id, status, processed_items, created_at, started_at, updated_at
        ))
    
    cursor.executemany('''
        INSERT OR IGNORE INTO scraping_queue (job_id, status, processed_items, created_at, started_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', queue_data)
    
    # Generar datos de scraping logs
    print("Generando datos de scraping logs...")
    log_levels = ["INFO", "WARNING", "ERROR"]
    log_messages = [
        "Job started successfully",
        "Processing website data",
        "Emails extracted successfully",
        "Connection timeout occurred",
        "Rate limit exceeded",
        "Job completed with warnings",
        "Database connection established",
        "Cache cleared successfully"
    ]
    
    logs_data = []
    for i in range(30):
        created_at = datetime.utcnow() - timedelta(hours=random.randint(0, 168))  # Última semana
        level = random.choice(log_levels)
        message = random.choice(log_messages)
        url = f"https://devactivo.com/page{i}" if random.choice([True, False]) else None
        job_id = f"job_{random.randint(1000, 9999)}" if random.choice([True, False]) else None
        
        logs_data.append((
            level, message, url, job_id, created_at
        ))
    
    cursor.executemany('''
        INSERT OR IGNORE INTO scraping_logs (level, message, url, job_id, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', logs_data)
    
    # Generar datos de estadísticas históricas
    print("Generando datos de estadísticas históricas...")
    
    # SystemStats
    for i in range(30):  # 30 días de datos
        timestamp = datetime.utcnow() - timedelta(days=i)
        cpu_usage = random.randint(10, 90)
        memory_usage = random.randint(100, 800)  # MB
        disk_usage = random.randint(5, 50)  # GB
        active_connections = random.randint(1, 20)
        
        cursor.execute('''
            INSERT OR IGNORE INTO system_stats (timestamp, cpu_usage, memory_usage, disk_usage, active_connections)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, cpu_usage, memory_usage, disk_usage, active_connections))
    
    # ScrapingStats
    for i in range(30):  # 30 días de datos
        timestamp = datetime.utcnow() - timedelta(days=i)
        urls_processed = random.randint(50, 500)
        success_rate = round(random.uniform(80.0, 99.9), 2)
        avg_response_time = random.randint(50, 500)
        errors_count = random.randint(0, 20)
        
        cursor.execute('''
            INSERT OR IGNORE INTO scraping_stats (timestamp, urls_processed, success_rate, avg_response_time, errors_count)
            VALUES (?, ?, ?, ?, ?)
        ''', (timestamp, urls_processed, success_rate, avg_response_time, errors_count))
    
    # JobStats
    for i in range(50):  # 50 jobs
        job_id = f"job_{random.randint(1000, 9999)}"
        duration = random.randint(60, 3600)  # 1 minuto a 1 hora
        efficiency = round(random.uniform(70.0, 99.9), 2)
        performance_history = json.dumps([
            {"timestamp": (datetime.utcnow() - timedelta(hours=j)).isoformat(), 
             "processed_items": random.randint(10, 100), 
             "success_rate": round(random.uniform(80.0, 99.9), 2)}
            for j in range(5)
        ])
        
        cursor.execute('''
            INSERT OR IGNORE INTO job_stats (job_id, duration, efficiency, performance_history)
            VALUES (?, ?, ?, ?)
        ''', (job_id, duration, efficiency, performance_history))
    
    # Guardar cambios y cerrar conexión
    conn.commit()
    conn.close()
    
    print("✅ Datos de prueba generados exitosamente")

def main():
    """Función principal."""
    print("🚀 Generando datos de prueba para el sistema de estadísticas...")
    print("=" * 60)
    
    try:
        generate_test_data()
        print("\n🎉 ¡Datos de prueba generados exitosamente!")
        print("\nAhora puedes ejecutar las pruebas de estadísticas para ver los datos en acción.")
        return 0
    except Exception as e:
        print(f"\n❌ Error al generar datos de prueba: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)