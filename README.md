# Generador de Leads

Sistema completo de generación de leads con scraping web, análisis de datos y panel de estadísticas en tiempo real.

## Características

- **Scraping Web Avanzado**: Extracción de datos de sitios web con configuración flexible
- **Gestión de Jobs**: Sistema de colas para procesar múltiples tareas de scraping
- **Panel de Estadísticas**: Visualización en tiempo real de métricas del sistema
- **API REST**: Endpoints para control y monitoreo del sistema
- **Interfaz de Escritorio**: Aplicación de escritorio con Tkinter para control del sistema
- **Sistema de Caching**: Mejora del rendimiento con caching inteligente
- **Logging Integrado**: Registro detallado de actividades y errores

## Requisitos

- Python 3.8 o superior
- Sistema operativo Linux (recomendado)
- Dependencias listadas en `requirements.txt`

## Instalación

1. Clonar el repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd leads-generator
   ```

2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   # o
   venv\Scripts\activate     # En Windows
   ```

3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Instalar dependencias del sistema (en Linux):
   ```bash
   sudo apt-get install python3-tk  # Para Tkinter
   ```

## Estructura del Proyecto

```
leads-generator/
├── backend/
│   ├── app/
│   │   ├── api/          # Endpoints de la API
│   │   ├── core/         # Componentes centrales (caching, logging, etc.)
│   │   ├── database/     # Modelos y acceso a base de datos
│   │   └── main.py       # Punto de entrada de la aplicación
│   ├── tests/            # Pruebas unitarias e integración
│   └── app_database.db   # Base de datos SQLite
├── frontend/
│   ├── components/       # Componentes de la interfaz
│   ├── config.py         # Configuración del frontend
│   ├── api_client.py     # Cliente para comunicarse con el backend
│   ├── widgets.py        # Widgets personalizados
│   └── main.py           # Aplicación principal de escritorio
├── docs/                 # Documentación
├── requirements.txt      # Dependencias del proyecto
├── run_app.py            # Script para ejecutar la aplicación completa
└── README.md             # Este archivo
```

## Ejecución

### Método 1: Usando el script de ejecución (recomendado)

```bash
python run_app.py
```

Este script iniciará automáticamente tanto el backend como el frontend.

### Método 2: Ejecución manual

1. **Iniciar el backend:**
   ```bash
   cd backend
   python -m uvicorn app.main:app --host 127.0.0.1 --port 800 --reload
   ```

2. **Iniciar el frontend:**
   ```bash
   cd frontend
   python main.py
   ```

## Funcionalidades Principales

### Scraping Web
- Configuración de URL inicial, profundidad y delay
- Soporte para múltiples idiomas
- Extracción de emails y datos de contacto
- Filtrado de contenido duplicado

### Gestión de Jobs
- Creación y control de jobs de scraping
- Pausa, reanudación y cancelación de jobs
- Priorización de jobs
- Monitoreo de progreso en tiempo real

### Panel de Estadísticas
- Métricas del sistema en tiempo real
- Estadísticas de scraping detalladas
- Rendimiento del sistema
- Historial de actividad

### API REST
- Endpoints para control de scraping
- Estadísticas del sistema
- Gestión de jobs
- Consulta de leads encontrados

## Endpoints de la API

### Control de Scraping
- `POST /api/v1/scraping/start` - Iniciar un nuevo job de scraping
- `POST /api/v1/scraping/stop/{job_id}` - Detener un job de scraping
- `GET /api/v1/scraping/status/{job_id}` - Obtener el estado de un job

### Estadísticas
- `GET /api/v1/stats/system` - Estadísticas del sistema
- `GET /api/v1/stats/scraping` - Estadísticas de scraping
- `GET /api/v1/stats/jobs/{job_id}` - Estadísticas de un job específico
- `GET /api/v1/stats/historical` - Datos históricos
- `GET /api/v1/stats/performance` - Métricas de rendimiento
- `GET /api/v1/stats/sources` - Estadísticas por fuente

### Control Avanzado de Jobs
- `POST /api/v1/jobs/{job_id}/pause` - Pausar un job
- `POST /api/v1/jobs/{job_id}/resume` - Reanudar un job
- `POST /api/v1/jobs/{job_id}/priority` - Actualizar prioridad de un job
- `GET /api/v1/jobs/{job_id}/progress` - Obtener progreso detallado
- `GET /api/v1/jobs/{job_id}/logs` - Obtener logs de un job
- `POST /api/v1/jobs/pause-all` - Pausar todos los jobs
- `POST /api/v1/jobs/resume-all` - Reanudar todos los jobs
- `POST /api/v1/jobs/cancel-active` - Cancelar todos los jobs activos

### Gestión de Cola
- `GET /api/v1/queue/status` - Obtener estado de la cola
- `POST /api/v1/queue/clear` - Limpiar cola de jobs pendientes

### Leads
- `GET /api/v1/leads` - Obtener leads encontrados
- `GET /api/v1/leads/export` - Exportar leads a CSV

## Pruebas

El sistema incluye scripts de prueba para verificar el funcionamiento de los endpoints:

```bash
cd backend
python test_stats_endpoints.py     # Prueba básica de endpoints
python test_realtime_stats.py      # Prueba de actualización en tiempo real
python test_stats_with_data.py     # Prueba con datos generados
```

## Documentación

La documentación de la API está disponible en:
- `docs/api/stats_endpoints.md` - Documentación de endpoints de estadísticas

## Contribución

1. Fork del repositorio
2. Crear una rama para la nueva funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de los cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Para reportar problemas o sugerencias, por favor abre un issue en el repositorio.