# Endpoints de Estadísticas

Documentación de los endpoints de estadísticas implementados en el sistema de leads generator.

## Endpoints Disponibles

### 1. Estadísticas del Sistema

**Endpoint:** `GET /api/v1/stats/system`

Obtiene estadísticas del sistema en tiempo real.

**Respuesta:**
```json
{
  "active_jobs": 4,
  "total_jobs_today": 0,
  "total_leads_today": 0,
  "total_emails_today": 0,
  "system_health": {
    "database_status": "healthy",
    "memory_usage_mb": 128.5,
    "cpu_usage_percent": 15.3,
    "disk_usage_gb": 15.2,
    "uptime_seconds": 3600
  },
  "recent_activity": [
    {
      "timestamp": "2023-05-15T10:30:00Z",
      "level": "INFO",
      "message": "Job completed successfully",
      "url": "https://example.com"
    }
  ],
  "performance_summary": {
    "avg_response_time": 120.5,
    "total_websites": 1000,
    "total_emails": 500,
    "success_rate": 95.5
  }
}
```

**Caching:** 30 segundos

### 2. Estadísticas de Scraping

**Endpoint:** `GET /api/v1/stats/scraping?period={period}`

Obtiene métricas detalladas de scraping.

**Parámetros:**
- `period` (opcional): Período de tiempo (hour, day, week, month). Por defecto: day

**Respuesta:**
```json
{
  "period": "day",
  "total_urls_processed": 150,
  "success_rate": 92.5,
  "avg_processing_time": 125.3,
  "domains_crawled": 25,
  "duplicates_filtered": 15,
  "urls_by_hour": [
    {
      "hour": 9,
      "count": 15
    },
    {
      "hour": 10,
      "count": 22
    }
  ],
  "top_domains": [
    {
      "domain": "example.com",
      "count": 50
    }
  ]
}
```

**Caching:** 60 segundos

### 3. Estadísticas de Jobs Específicos

**Endpoint:** `GET /api/v1/stats/jobs/{job_id}`

Obtiene estadísticas específicas de un job.

**Parámetros:**
- `job_id`: ID del job

**Respuesta:**
```json
{
  "job_id": "abc123",
  "duration": 300,
  "efficiency": 85.5,
  "status_distribution": {
    "pending": 0,
    "processing": 0,
    "completed": 50,
    "failed": 2,
    "paused": 0,
    "cancelled": 0
  },
  "performance_history": [
    {
      "timestamp": "2023-05-15T10:30:00Z",
      "processed_items": 10,
      "success_rate": 95.0
    }
  ]
}
```

**Caching:** 30 segundos

### 4. Estadísticas Históricas

**Endpoint:** `GET /api/v1/stats/historical?period={period}`

Obtiene datos históricos con filtros de fecha.

**Parámetros:**
- `period` (opcional): Período de tiempo (day, week, month, year). Por defecto: week

**Respuesta:**
```json
{
  "period": "week",
  "data": [
    {
      "timestamp": "2023-05-08T0:00:00Z",
      "websites": 150,
      "emails": 75,
      "jobs": 25
    },
    {
      "timestamp": "2023-05-09T00:00:00Z",
      "websites": 180,
      "emails": 90,
      "jobs": 30
    }
  ]
}
```

**Caching:** 5 minutos

### 5. Estadísticas de Rendimiento

**Endpoint:** `GET /api/v1/stats/performance`

Obtiene métricas de rendimiento detalladas.

**Respuesta:**
```json
{
  "timestamp": "2023-05-15T10:30:00Z",
  "scraping_performance": {
    "requests_per_second": 5.2,
    "avg_response_time": 120.5,
    "median_response_time": 110.2,
    "p95_response_time": 200.8,
    "error_rate_percent": 2.5
  },
  "system_resources": {
    "cpu_percent": 15.3,
    "memory_percent": 45.2,
    "disk_io_read_mb": 128.5,
    "disk_io_write_mb": 64.2,
    "network_rx_mb": 10.5,
    "network_tx_mb": 5.3
  },
  "database_performance": {
    "connections_active": 5,
    "queries_per_second": 25.3,
    "avg_query_time": 0.015,
    "cache_hit_rate": 0.85
  },
  "queue_status": {
    "pending_urls": 100,
    "processing_urls": 10,
    "completed_urls": 500,
    "failed_urls": 5
  }
}
```

**Caching:** 30 segundos

### 6. Estadísticas por Fuente

**Endpoint:** `GET /api/v1/stats/sources`

Obtiene estadísticas por fuente/dominio.

**Respuesta:**
```json
{
  "sources": [
    {
      "domain": "example.com",
      "websites_count": 150,
      "emails_count": 75,
      "avg_quality_score": 8.5
    }
  ],
  "top_sources": [
    {
      "domain": "example.com",
      "count": 150
    }
  ]
}
```

**Caching:** 5 minutos

## Sistema de Caching

Todos los endpoints de estadísticas implementan un sistema de caching para mejorar el rendimiento:

- **Estadísticas del sistema:** 30 segundos
- **Estadísticas de scraping:** 60 segundos
- **Estadísticas de jobs:** 30 segundos
- **Estadísticas históricas:** 5 minutos
- **Estadísticas de rendimiento:** 30 segundos
- **Estadísticas por fuente:** 5 minutos

## Integración con Logging

El sistema de estadísticas está integrado con el sistema de logging existente, registrando métricas importantes en los logs para facilitar el monitoreo y la depuración.

## Actualización en Tiempo Real

Las estadísticas se actualizan en tiempo real, con mecanismos de caching inteligentes que equilibran la frescura de los datos con el rendimiento del sistema.