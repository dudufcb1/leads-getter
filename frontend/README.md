# Frontend de Escritorio - Leads Generator

Interfaz gráfica de escritorio para el sistema de generación de leads con scraper avanzado.

## Características

- Panel de control para configurar y ejecutar trabajos de scraping
- Visualización en tiempo real de estadísticas del proceso
- Tabla de leads encontrados con filtros y paginación
- Exportación de leads a archivos CSV
- Monitoreo de logs del sistema

## Requisitos

- Python 3.8 o superior
- Tkinter (generalmente incluido con Python)
- Acceso al backend del sistema de generación de leads

## Instalación

1. Asegúrate de tener el entorno virtual activado:
   ```bash
   source ../.venv/bin/activate  # En Linux/macOS
   ```

2. El frontend utiliza los mismos requisitos que el backend, por lo que no necesitas instalar dependencias adicionales.

## Uso

Para ejecutar la aplicación de escritorio:

```bash
python run_frontend.py
```

## Estructura del Proyecto

```
frontend/
├── __init__.py
├── config.py          # Configuración de la aplicación
├── api_client.py      # Cliente para comunicarse con el backend
├── widgets.py         # Widgets personalizados de Tkinter
├── main.py            # Aplicación principal
└── run_frontend.py    # Punto de entrada
```

## Funcionalidades

### 1. Control de Scraping
- Configuración de URL inicial, profundidad y delay
- Selección de idiomas para el scraping
- Botones para iniciar y detener el proceso
- Visualización de estadísticas en tiempo real

### 2. Leads Encontrados
- Tabla paginada con leads encontrados
- Filtros por idioma y dominio
- Exportación a CSV

### 3. Estadísticas
- Métricas del sistema en tiempo real
- Información de recursos (memoria, CPU, disco)

### 4. Logs
- Visualización de logs del sistema
- Área de texto con scroll para revisar eventos

## Desarrollo

### Estructura de Código

- `config.py`: Constantes y configuraciones globales
- `api_client.py`: Cliente HTTP para comunicarse con el backend
- `widgets.py`: Componentes personalizados de la interfaz
- `main.py`: Lógica principal de la aplicación

### Consideraciones Técnicas

- La aplicación se comunica con el backend a través de la API REST
- Las operaciones de red se ejecutan en hilos separados para no bloquear la interfaz
- Se utiliza un sistema de actualización periódica para mantener las estadísticas actualizadas
- La interfaz se adapta a diferentes tamaños de ventana

## Solución de Problemas

### No se puede conectar con la API
- Verifica que el backend esté ejecutándose en `http://127.0.0.1:8000`
- Comprueba que no haya conflictos de red o firewall

### La interfaz no responde
- Las operaciones de red se ejecutan en hilos separados, pero operaciones muy pesadas en la interfaz pueden causar bloqueos
- Reinicia la aplicación si el problema persiste

### Problemas con la visualización
- En algunos entornos Linux, puede haber diferencias en la apariencia de los widgets
- Asegúrate de tener las dependencias de Tkinter correctamente instaladas