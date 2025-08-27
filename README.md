# Leads Generator - Advanced Scraper

Un sistema avanzado de generación de leads mediante web scraping con capacidades de scraping encadenado, detección inteligente de emails, y monitoreo completo.

## 🚀 Características Principales

### Scraping Avanzado
- **Scraping encadenado** con control de profundidad configurable
- **Detección avanzada de emails** con múltiples patrones y validación
- **Rotación de user-agents** para evitar bloqueos
- **Rate limiting adaptativo** por dominio
- **Manejo robusto de errores** con reintentos y backoff exponencial

### Calidad de Datos
- **Filtrado por idioma** con detección automática
- **Deduplicación inteligente** de contenido
- **Puntuación de calidad** para leads y emails
- **Validación de formato** de emails

### Monitoreo y Control
- **Logging completo** en base de datos
- **Estadísticas en tiempo real** del proceso de scraping
- **API REST** para control remoto
- **Sesiones de scraping** con seguimiento detallado

## 📋 Requisitos del Sistema

- **Python**: 3.8 o superior
- **Sistema Operativo**: Linux (desarrollo y testing)
- **Memoria**: Mínimo 512MB RAM
- **Espacio en disco**: 100MB para base de datos y logs

### Dependencias del Sistema (Linux)

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3-tk python3-dev build-essential

# Fedora/CentOS
sudo dnf install python3-tkinter python3-devel gcc

# Arch Linux
sudo pacman -S tk python
```

## 🛠️ Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <repository-url>
   cd leads-generator
   ```

2. **Crear entorno virtual**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   # o
   .venv\Scripts\activate     # Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Inicializar base de datos**
   ```bash
   cd backend
   python -c "from app.database.database import init_db; init_db()"
   ```

## 🚀 Uso Básico

### Iniciar el Servidor Backend

```bash
cd backend
python run_backend.py
```

El servidor estará disponible en `http://127.0.0.1:8000`

### Ejemplo de Uso de la API

```python
import requests

# Iniciar trabajo de scraping avanzado
response = requests.post('http://localhost:8000/api/jobs', json={
    "start_url": "https://example.com",
    "config": {
        "max_depth": 3,
        "languages": ["es", "en"],
        "delay": 2.0,
        "user_agent_rotation": True,
        "rate_limiting": True
    }
})

job_id = response.json()['job_id']

# Monitorear progreso
status = requests.get(f'http://localhost:8000/api/jobs/{job_id}').json()
print(f"Estado: {status['status']}")
print(f"URLs procesadas: {status['stats']['processed_urls']}")
```

## ⚙️ Configuración Avanzada

### Parámetros de Scraping

| Parámetro | Descripción | Valor por Defecto |
|-----------|-------------|-------------------|
| `MAX_DEPTH` | Profundidad máxima de crawling | 3 |
| `DOWNLOAD_DELAY` | Retraso entre requests (segundos) | 1.0 |
| `CONCURRENT_REQUESTS` | Requests concurrentes | 16 |
| `DOWNLOAD_TIMEOUT` | Timeout de requests (segundos) | 30 |
| `RETRY_TIMES` | Número máximo de reintentos | 3 |

### Configuración de Calidad

```python
# En backend/app/scraper/settings.py
SUPPORTED_LANGUAGES = ['es', 'en', 'fr', 'de']
MIN_CONTENT_LENGTH = 100
MIN_EMAIL_QUALITY_SCORE = 0.5
```

## 📊 Monitoreo

### Estadísticas en Tiempo Real

```bash
# Obtener estadísticas del sistema
curl http://localhost:8000/api/stats
```

### Logs de Base de Datos

Los logs se almacenan en la tabla `scraping_logs` con las siguientes categorías:
- `request`: Detalles de requests HTTP
- `parsing`: Extracción y procesamiento de contenido
- `error`: Errores y excepciones
- `performance`: Métricas de rendimiento

## 🔧 Solución de Problemas

### Problemas Comunes

#### Error de Memoria
```bash
# Reducir requests concurrentes
export CONCURRENT_REQUESTS=8
```

#### Bloqueos por Anti-Bot
```python
# Aumentar delays y habilitar rotación
config = {
    "delay": 3.0,
    "user_agent_rotation": True,
    "rate_limiting": True
}
```

#### Emails de Baja Calidad
```python
# Ajustar filtros de calidad
config = {
    "min_email_quality_score": 0.7,
    "languages": ["es"],
    "min_content_length": 200
}
```

### Debugging

```bash
# Ejecutar con logging detallado
export LOG_LEVEL=DEBUG
python run_backend.py
```

## 📚 Documentación

- **[Plan Técnico](docs/technical_plan.md)**: Arquitectura general del sistema
- **[Scraper Avanzado](docs/advanced_scraper.md)**: Documentación completa de características avanzadas
- **[API Reference](docs/api_reference.md)**: Referencia completa de la API REST

## 🏗️ Arquitectura

```
leads-generator/
├── backend/                 # Servidor y lógica de negocio
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   ├── scraper/        # Motor de Scrapy
│   │   ├── database/       # Modelos y conexión DB
│   │   └── core/           # Configuración
│   └── requirements.txt
├── docs/                   # Documentación
└── README.md
```

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte técnico o preguntas:
- Revisar la [documentación avanzada](docs/advanced_scraper.md)
- Consultar los [logs de troubleshooting](docs/troubleshooting.md)
- Abrir un issue en el repositorio

---

**Nota**: Este sistema está diseñado para uso ético y respetuoso con los términos de servicio de los sitios web. Asegúrate de cumplir con las leyes locales y las políticas de los sitios que visites.