# API Reference - Leads Generator

Referencia completa de la API REST para el sistema de generación de leads con scraper avanzado.

## Base URL

```
http://127.0.0.1:8000/api/v1
```

## Autenticación

La API actualmente no requiere autenticación. En futuras versiones se implementará autenticación basada en tokens.

## Endpoints

### Jobs (Trabajos)

#### POST /jobs
Inicia un nuevo trabajo de scraping avanzado.

**Request Body:**
```json
{
    "start_url": "https://example.com",
    "config": {
        "max_depth": 3,
        "languages": ["es", "en"],
        "delay": 2.0,
        "user_agent_rotation": true,
        "rate_limiting": true,
        "respect_robots": true,
        "download_timeout": 30,
        "retry_times": 3,
        "min_content_length": 100,
        "min_email_quality_score": 0.5
    }
}
```

**Parámetros de Configuración:**

| Parámetro | Tipo | Descripción | Valor por Defecto |
|-----------|------|-------------|-------------------|
| `max_depth` | integer | Profundidad máxima de crawling | 3 |
| `languages` | array | Idiomas a filtrar (vacío = todos) | [] |
| `delay` | float | Retraso entre requests (segundos) | 1.0 |
| `user_agent_rotation` | boolean | Rotar user-agents | true |
| `rate_limiting` | boolean | Habilitar rate limiting | true |
| `respect_robots` | boolean | Respetar robots.txt | true |
| `download_timeout` | integer | Timeout de requests (segundos) | 30 |
| `retry_times` | integer | Número máximo de reintentos | 3 |
| `min_content_length` | integer | Longitud mínima de contenido | 100 |
| `min_email_quality_score` | float | Score mínimo de calidad de email (0-1) | 0.5 |

**Response (202 Accepted):**
```json
{
    "job_id": "uuid-1234-abcd",
    "status": "starting",
    "message": "Advanced scraping job started.",
    "config": {
        "max_depth": 3,
        "languages": ["es", "en"],
        "delay": 2.0,
        "user_agent_rotation": true,
        "rate_limiting": true,
        "respect_robots": true,
        "download_timeout": 30,
        "retry_times": 3,
        "min_content_length": 100,
        "min_email_quality_score": 0.5
    }
}
```

**Códigos de Error:**
- `400 Bad Request`: Configuración inválida
- `500 Internal Server Error`: Error del servidor

#### GET /jobs/{job_id}
Obtiene el estado y estadísticas de un trabajo específico.

**Parámetros de URL:**
- `job_id` (string, required): ID del trabajo

**Response (200 OK):**
```json
{
    "job_id": "uuid-1234-abcd",
    "status": "running",
    "start_time": "2023-10-27T10:00:00Z",
    "end_time": null,
    "config": { ... },
    "stats": {
        "processed_urls": 150,
        "queue_size": 45,
        "leads_found": 23,
        "emails_found": 45,
        "errors_count": 2,
        "avg_response_time": 1.2,
        "current_depth": 2,
        "domains_crawled": 12,
        "duplicates_filtered": 8
    },
    "performance": {
        "requests_per_minute": 25.3,
        "memory_usage_mb": 89,
        "cpu_usage_percent": 15.2,
        "active_threads": 8
    },
    "errors": [
        {
            "timestamp": "2023-10-27T10:15:00Z",
            "url": "https://example.com/page",
            "error_type": "timeout",
            "message": "Request timeout after 30 seconds"
        }
    ]
}
```

**Estados Posibles:**
- `starting`: Trabajo iniciándose
- `running`: Trabajo en ejecución
- `completed`: Trabajo completado exitosamente
- `failed`: Trabajo fallido
- `stopped`: Trabajo detenido por usuario

#### DELETE /jobs/{job_id}
Detiene un trabajo en ejecución.

**Parámetros de URL:**
- `job_id` (string, required): ID del trabajo

**Response (200 OK):**
```json
{
    "job_id": "uuid-1234-abcd",
    "status": "stopping",
    "message": "Scraping job is being stopped."
}
```

### Leads

#### GET /leads
Obtiene la lista de leads encontrados con paginación y filtros.

**Query Parameters:**

| Parámetro | Tipo | Descripción | Valor por Defecto |
|-----------|------|-------------|-------------------|
| `page` | integer | Número de página | 1 |
| `limit` | integer | Elementos por página | 50 |
| `language` | string | Filtrar por idioma | null |
| `domain` | string | Filtrar por dominio | null |
| `min_score` | float | Score mínimo de calidad | 0.0 |
| `sort_by` | string | Campo para ordenar (url, score, created_at) | created_at |
| `sort_order` | string | Orden (asc, desc) | desc |

**Response (200 OK):**
```json
{
    "pagination": {
        "total_items": 234,
        "total_pages": 5,
        "current_page": 1,
        "per_page": 50,
        "has_next": true,
        "has_prev": false
    },
    "leads": [
        {
            "id": 1,
            "url": "https://example.com",
            "domain": "example.com",
            "title": "Example Company",
            "description": "Company description...",
            "language": "es",
            "language_confidence": 0.95,
            "quality_score": 0.85,
            "emails_count": 3,
            "status": "processed",
            "depth_level": 1,
            "source_url": "https://initial-site.com",
            "created_at": "2023-10-27T10:00:00Z",
            "updated_at": "2023-10-27T10:30:00Z",
            "session_id": "session-123",
            "last_crawled": "2023-10-27T10:30:00Z",
            "crawl_count": 1
        }
    ],
    "filters_applied": {
        "language": "es",
        "min_score": 0.5
    }
}
```

#### GET /leads/{lead_id}
Obtiene detalles específicos de un lead incluyendo emails asociados.

**Parámetros de URL:**
- `lead_id` (integer, required): ID del lead

**Response (200 OK):**
```json
{
    "id": 1,
    "url": "https://example.com",
    "domain": "example.com",
    "title": "Example Company",
    "description": "Company description...",
    "language": "es",
    "language_confidence": 0.95,
    "quality_score": 0.85,
    "status": "processed",
    "depth_level": 1,
    "source_url": "https://initial-site.com",
    "created_at": "2023-10-27T10:00:00Z",
    "updated_at": "2023-10-27T10:30:00Z",
    "emails": [
        {
            "id": 1,
            "email": "contact@example.com",
            "quality_score": 0.9,
            "validation_status": "valid",
            "source_page": "https://example.com/contact",
            "source_context": "Contact us at: contact@example.com",
            "created_at": "2023-10-27T10:15:00Z"
        }
    ]
}
```

### Emails

#### GET /emails
Obtiene lista de emails con filtros avanzados.

**Query Parameters:**

| Parámetro | Tipo | Descripción | Valor por Defecto |
|-----------|------|-------------|-------------------|
| `page` | integer | Número de página | 1 |
| `limit` | integer | Elementos por página | 50 |
| `domain` | string | Filtrar por dominio | null |
| `min_score` | float | Score mínimo de calidad | 0.0 |
| `validation_status` | string | Estado de validación (valid, invalid, pending) | null |
| `sort_by` | string | Campo para ordenar | quality_score |
| `sort_order` | string | Orden (asc, desc) | desc |

**Response (200 OK):**
```json
{
    "pagination": {
        "total_items": 456,
        "total_pages": 10,
        "current_page": 1,
        "per_page": 50
    },
    "emails": [
        {
            "id": 1,
            "email": "contact@example.com",
            "domain": "example.com",
            "quality_score": 0.9,
            "validation_status": "valid",
            "source_page": "https://example.com/contact",
            "source_context": "Contact us at: contact@example.com",
            "lead_id": 1,
            "created_at": "2023-10-27T10:15:00Z",
            "session_id": "session-123"
        }
    ]
}
```

### Statistics (Estadísticas)

#### GET /stats
Obtiene estadísticas generales del sistema.

**Response (200 OK):**
```json
{
    "active_jobs": 2,
    "total_jobs_today": 15,
    "total_leads_today": 234,
    "total_emails_today": 456,
    "system_health": {
        "database_status": "healthy",
        "memory_usage_mb": 245,
        "cpu_usage_percent": 12.5,
        "disk_usage_gb": 2.1,
        "uptime_seconds": 3600
    },
    "recent_activity": [
        {
            "timestamp": "2023-10-27T10:45:00Z",
            "job_id": "uuid-1234-abcd",
            "action": "url_processed",
            "details": "Processed https://example.com/page1",
            "stats": {
                "leads_found": 1,
                "emails_found": 2
            }
        }
    ],
    "performance_summary": {
        "avg_response_time": 1.2,
        "requests_per_minute": 25.3,
        "error_rate_percent": 2.1,
        "success_rate_percent": 97.9
    }
}
```

#### GET /stats/jobs
Obtiene estadísticas detalladas de trabajos.

**Query Parameters:**
- `period` (string): Período de tiempo (hour, day, week, month) - Default: day

**Response (200 OK):**
```json
{
    "period": "day",
    "total_jobs": 15,
    "successful_jobs": 13,
    "failed_jobs": 2,
    "avg_duration_seconds": 450,
    "jobs_by_status": {
        "completed": 13,
        "failed": 2,
        "running": 0
    },
    "jobs_by_hour": [
        {"hour": "00", "count": 0},
        {"hour": "01", "count": 0},
        // ... 24 hours
    ],
    "top_error_types": [
        {"error_type": "timeout", "count": 5},
        {"error_type": "connection_error", "count": 3}
    ]
}
```

#### GET /stats/performance
Obtiene métricas de rendimiento detalladas.

**Response (200 OK):**
```json
{
    "timestamp": "2023-10-27T10:45:00Z",
    "scraping_performance": {
        "requests_per_second": 0.42,
        "avg_response_time": 1.2,
        "median_response_time": 0.8,
        "p95_response_time": 3.5,
        "error_rate_percent": 2.1
    },
    "system_resources": {
        "cpu_percent": 12.5,
        "memory_percent": 15.2,
        "disk_io_read_mb": 45.2,
        "disk_io_write_mb": 23.1,
        "network_rx_mb": 12.5,
        "network_tx_mb": 8.3
    },
    "database_performance": {
        "connections_active": 3,
        "queries_per_second": 25.3,
        "avg_query_time": 0.015,
        "cache_hit_rate": 0.85
    },
    "queue_status": {
        "pending_urls": 150,
        "processing_urls": 8,
        "completed_urls": 2340,
        "failed_urls": 45
    }
}
```

### Logs

#### GET /logs
Obtiene logs del sistema con filtrado avanzado.

**Query Parameters:**

| Parámetro | Tipo | Descripción | Valor por Defecto |
|-----------|------|-------------|-------------------|
| `page` | integer | Número de página | 1 |
| `limit` | integer | Elementos por página | 100 |
| `level` | string | Nivel de log (DEBUG, INFO, WARNING, ERROR) | null |
| `category` | string | Categoría de log | null |
| `session_id` | string | ID de sesión | null |
| `start_date` | string | Fecha inicio (ISO 8601) | null |
| `end_date` | string | Fecha fin (ISO 8601) | null |

**Response (200 OK):**
```json
{
    "pagination": {
        "total_items": 1234,
        "total_pages": 13,
        "current_page": 1,
        "per_page": 100
    },
    "logs": [
        {
            "id": 1,
            "session_id": "session-123",
            "timestamp": "2023-10-27T10:30:00Z",
            "level": "INFO",
            "category": "request",
            "message": "Successfully processed URL: https://example.com",
            "url": "https://example.com",
            "metadata": {
                "response_time": 1.2,
                "status_code": 200,
                "content_length": 15432
            }
        }
    ],
    "filters_applied": {
        "level": "INFO",
        "category": "request"
    }
}
```

## Códigos de Estado HTTP

### 2xx Success
- `200 OK`: Solicitud exitosa
- `202 Accepted`: Solicitud aceptada para procesamiento

### 4xx Client Error
- `400 Bad Request`: Datos de solicitud inválidos
- `404 Not Found`: Recurso no encontrado
- `429 Too Many Requests`: Rate limit excedido

### 5xx Server Error
- `500 Internal Server Error`: Error interno del servidor
- `503 Service Unavailable`: Servicio no disponible

## Rate Limiting

La API implementa rate limiting automático:
- **Requests por minuto**: 60 por IP
- **Headers de respuesta**:
  - `X-RateLimit-Limit`: Límite máximo
  - `X-RateLimit-Remaining`: Requests restantes
  - `X-RateLimit-Reset`: Timestamp de reset

## Formatos de Datos

### Fechas
Todas las fechas están en formato ISO 8601 UTC:
```
2023-10-27T10:30:00Z
```

### Scores de Calidad
Los scores de calidad son valores flotantes entre 0.0 y 1.0:
- `0.0`: Calidad muy baja
- `0.5`: Calidad media
- `1.0`: Calidad excelente

### Estados de Validación de Email
- `pending`: Pendiente de validación
- `valid`: Email válido
- `invalid`: Email inválido
- `unknown`: No se pudo determinar

## Ejemplos de Uso

### Python con requests

```python
import requests
import time

# Iniciar trabajo
response = requests.post('http://localhost:8000/api/v1/jobs', json={
    "start_url": "https://example.com",
    "config": {
        "max_depth": 2,
        "languages": ["es", "en"],
        "delay": 1.5
    }
})

job_id = response.json()['job_id']

# Monitorear progreso
while True:
    status = requests.get(f'http://localhost:8000/api/v1/jobs/{job_id}').json()
    print(f"Estado: {status['status']}")
    print(f"URLs procesadas: {status['stats']['processed_urls']}")

    if status['status'] in ['completed', 'failed', 'stopped']:
        break

    time.sleep(10)

# Obtener resultados
leads = requests.get('http://localhost:8000/api/v1/leads').json()
print(f"Leads encontrados: {len(leads['leads'])}")
```

### JavaScript/Node.js

```javascript
const axios = require('axios');

async function startScraping() {
    try {
        // Iniciar trabajo
        const response = await axios.post('http://localhost:8000/api/v1/jobs', {
            start_url: 'https://example.com',
            config: {
                max_depth: 3,
                languages: ['es', 'en'],
                delay: 2.0
            }
        });

        const jobId = response.data.job_id;
        console.log(`Trabajo iniciado: ${jobId}`);

        // Monitorear
        let status;
        do {
            await new Promise(resolve => setTimeout(resolve, 5000));
            status = await axios.get(`http://localhost:8000/api/v1/jobs/${jobId}`);
            console.log(`Estado: ${status.data.status}`);
        } while (!['completed', 'failed', 'stopped'].includes(status.data.status));

        // Obtener leads
        const leads = await axios.get('http://localhost:8000/api/v1/leads');
        console.log(`Leads encontrados: ${leads.data.leads.length}`);

    } catch (error) {
        console.error('Error:', error.response?.data || error.message);
    }
}

startScraping();
```

### cURL

```bash
# Iniciar trabajo
curl -X POST http://localhost:8000/api/v1/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "start_url": "https://example.com",
    "config": {
      "max_depth": 2,
      "languages": ["es", "en"],
      "delay": 1.5
    }
  }'

# Obtener estado (reemplazar JOB_ID)
curl http://localhost:8000/api/v1/jobs/JOB_ID

# Obtener leads
curl http://localhost:8000/api/v1/leads

# Obtener estadísticas
curl http://localhost:8000/api/v1/stats
```

## Webhooks (Futuro)

En versiones futuras, la API soportará webhooks para notificaciones en tiempo real:

```json
{
    "event": "job_completed",
    "job_id": "uuid-1234-abcd",
    "timestamp": "2023-10-27T10:30:00Z",
    "data": {
        "leads_found": 23,
        "emails_found": 45,
        "duration_seconds": 450
    }
}
```

## Versionado

La API utiliza versionado en la URL:
- `v1`: Versión actual (esta documentación)

## Deprecations

No hay funcionalidades deprecadas en la versión actual.

## Changelog

### v1.0.0
- API inicial con soporte completo para scraper avanzado
- Endpoints para trabajos, leads, emails, estadísticas y logs
- Rate limiting y manejo de errores robusto
- Documentación completa de la API