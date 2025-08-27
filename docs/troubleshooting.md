# Guía de Solución de Problemas

Esta guía proporciona soluciones para problemas comunes que pueden surgir al usar el sistema de generación de leads con scraper avanzado.

## Problemas de Instalación

### Error: "python3-tk not found"

**Síntomas:**
```
ImportError: No module named 'tkinter'
```

**Soluciones:**

Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

Fedora/CentOS:
```bash
sudo dnf install python3-tkinter
```

Arch Linux:
```bash
sudo pacman -S tk
```

### Error de Dependencias

**Síntomas:**
```
ModuleNotFoundError: No module named 'scrapy'
```

**Solución:**
```bash
# Activar entorno virtual
source .venv/bin/activate

# Instalar dependencias
pip install -r backend/requirements.txt

# Verificar instalación
pip list | grep scrapy
```

### Problemas de Base de Datos

**Síntomas:**
```
sqlite3.OperationalError: no such table: websites
```

**Solución:**
```bash
cd backend
python -c "from app.database.database import init_db; init_db()"
```

## Problemas de Scraping

### Alto Porcentaje de Errores

**Causas posibles:**
- Servidores bloqueando requests
- Problemas de conectividad
- Configuración demasiado agresiva

**Soluciones:**

1. **Aumentar delays:**
   ```python
   config = {
       "delay": 3.0,
       "rate_limiting": True
   }
   ```

2. **Habilitar rotación de user-agents:**
   ```python
   config = {
       "user_agent_rotation": True
   }
   ```

3. **Reducir requests concurrentes:**
   ```bash
   export CONCURRENT_REQUESTS=8
   ```

### Pocos Leads Encontrados

**Causas posibles:**
- Filtros demasiado restrictivos
- URLs de baja calidad
- Problemas de detección de idioma

**Soluciones:**

1. **Relajar filtros de calidad:**
   ```python
   config = {
       "min_email_quality_score": 0.3,
       "min_content_length": 50
   }
   ```

2. **Deshabilitar filtrado de idioma:**
   ```python
   config = {
       "languages": []
   }
   ```

3. **Verificar URLs iniciales:**
   - Usar URLs de páginas con contenido rico
   - Evitar páginas de inicio simples

### Errores de Timeout

**Síntomas:**
```
twisted.internet.error.TimeoutError
```

**Soluciones:**

1. **Aumentar timeout:**
   ```python
   config = {
       "download_timeout": 60
   }
   ```

2. **Reducir concurrencia:**
   ```bash
   export CONCURRENT_REQUESTS=4
   ```

3. **Verificar conectividad de red**

### Problemas de Memoria

**Síntomas:**
```
MemoryError
```

**Soluciones:**

1. **Reducir requests concurrentes:**
   ```bash
   export CONCURRENT_REQUESTS=8
   ```

2. **Limitar profundidad:**
   ```python
   config = {
       "max_depth": 2
   }
   ```

3. **Monitorear uso de memoria:**
   ```bash
   python -c "import psutil; print(f'Memoria: {psutil.virtual_memory().percent}%')"
   ```

## Problemas de la API

### Error 500 Internal Server Error

**Causas posibles:**
- Problemas de base de datos
- Errores en el código del scraper
- Configuración incorrecta

**Solución:**
```bash
# Revisar logs
tail -f /var/log/leads-generator.log

# Reiniciar servidor
cd backend
python run_backend.py
```

### Error de Conexión

**Síntomas:**
```
Connection refused
```

**Soluciones:**

1. **Verificar que el servidor esté ejecutándose:**
   ```bash
   ps aux | grep run_backend.py
   ```

2. **Verificar puerto:**
   ```bash
   netstat -tlnp | grep 8000
   ```

3. **Reiniciar servidor:**
   ```bash
   cd backend
   python run_backend.py
   ```

### Errores de Rate Limiting

**Síntomas:**
```
HTTP 429 Too Many Requests
```

**Soluciones:**

1. **Aumentar delays:**
   ```python
   config = {
       "delay": 5.0,
       "rate_limiting": True
   }
   ```

2. **Reducir concurrencia:**
   ```bash
   export CONCURRENT_REQUESTS=1
   ```

## Problemas de Calidad de Datos

### Emails Inválidos

**Causas posibles:**
- Patrones de detección demasiado permisivos
- Contenido mal formateado

**Soluciones:**

1. **Aumentar score mínimo:**
   ```python
   config = {
       "min_email_quality_score": 0.8
   }
   ```

2. **Usar URLs más específicas:**
   - Preferir páginas de contacto
   - Evitar blogs y foros

### Duplicados Excesivos

**Causas posibles:**
- Configuración de deduplicación
- URLs similares

**Soluciones:**

1. **Mejorar configuración de deduplicación:**
   ```python
   # En settings.py
   DUPEFILTER_DEBUG = True
   ```

2. **Usar URLs más variadas**

### Problemas de Idioma

**Síntomas:**
- Contenido en idiomas no deseados
- Detección incorrecta de idioma

**Soluciones:**

1. **Ajustar lista de idiomas:**
   ```python
   config = {
       "languages": ["es", "en"]
   }
   ```

2. **Deshabilitar filtrado:**
   ```python
   config = {
       "languages": []
   }
   ```

## Problemas de Rendimiento

### Scraping Lento

**Causas posibles:**
- Delays demasiado altos
- Problemas de red
- Servidores lentos

**Soluciones:**

1. **Optimizar delays:**
   ```python
   config = {
       "delay": 1.0
   }
   ```

2. **Aumentar concurrencia:**
   ```bash
   export CONCURRENT_REQUESTS=32
   ```

3. **Usar conexiones más rápidas**

### Alto Uso de CPU

**Causas posibles:**
- Procesamiento intensivo
- Muchos threads

**Soluciones:**

1. **Reducir concurrencia:**
   ```bash
   export CONCURRENT_REQUESTS=16
   ```

2. **Optimizar expresiones regulares:**
   - Usar patrones más específicos
   - Precompilar regex

## Problemas de Monitoreo

### Logs No Aparecen

**Causas posibles:**
- Configuración de logging incorrecta
- Problemas de permisos

**Soluciones:**

1. **Verificar configuración:**
   ```python
   # En settings.py
   LOG_LEVEL = 'DEBUG'
   LOG_TO_DATABASE = True
   ```

2. **Verificar permisos de base de datos:**
   ```bash
   ls -la leads.db
   ```

### Estadísticas Incorrectas

**Causas posibles:**
- Problemas de sincronización
- Errores en el cálculo

**Soluciones:**

1. **Reiniciar sesión de scraping**
2. **Verificar integridad de base de datos:**
   ```bash
   sqlite3 leads.db "PRAGMA integrity_check;"
   ```

## Problemas del Sistema Operativo

### Linux Específicos

#### Error: "Too many open files"

**Solución:**
```bash
# Aumentar límite de archivos abiertos
ulimit -n 4096

# O permanentemente en /etc/security/limits.conf
* soft nofile 4096
* hard nofile 8192
```

#### Error: "Address already in use"

**Solución:**
```bash
# Matar proceso en puerto 8000
sudo lsof -ti:8000 | xargs kill -9

# O encontrar proceso
sudo netstat -tlnp | grep 8000
```

### Problemas de Red

#### DNS Resolution Fails

**Soluciones:**

1. **Verificar conectividad:**
   ```bash
   ping 8.8.8.8
   ```

2. **Usar DNS diferentes:**
   ```bash
   echo "nameserver 1.1.1.1" >> /etc/resolv.conf
   ```

3. **Configurar timeout de DNS:**
   ```python
   # En settings.py
   DNSCACHE_ENABLED = True
   DNS_TIMEOUT = 10
   ```

## Debugging Avanzado

### Habilitar Debug Mode

```bash
export SCRAPY_DEBUG=1
export LOG_LEVEL=DEBUG
python run_backend.py
```

### Capturar Requests HTTP

```python
# En middlewares.py, descomentar:
# import logging
# logging.getLogger("scrapy.core.engine").setLevel(logging.DEBUG)
```

### Perfilado de Rendimiento

```bash
# Instalar py-spy
pip install py-spy

# Ejecutar perfilado
py-spy top --pid $(pgrep -f run_backend.py)
```

### Logs de Base de Datos Detallados

```sql
-- Ver logs recientes
SELECT * FROM scraping_logs
WHERE timestamp > datetime('now', '-1 hour')
ORDER BY timestamp DESC;

-- Contar errores por categoría
SELECT category, level, COUNT(*) as count
FROM scraping_logs
GROUP BY category, level
ORDER BY count DESC;
```

## Contacto y Soporte

Si los problemas persisten después de seguir esta guía:

1. Revisa los logs completos
2. Incluye información del sistema:
   ```bash
   uname -a
   python --version
   pip list | grep -E "(scrapy|fastapi|uvicorn)"
   ```
3. Abre un issue con:
   - Descripción del problema
   - Pasos para reproducir
   - Logs relevantes
   - Configuración usada

## Prevención

### Mejores Prácticas

1. **Monitoreo continuo:**
   ```bash
   # Script de monitoreo básico
   watch -n 60 'curl -s http://localhost:8000/api/stats | jq .system_health'
   ```

2. **Backups regulares:**
   ```bash
   # Backup diario
   crontab -e
   0 2 * * * sqlite3 leads.db ".backup /backup/leads_$(date +\%Y\%m\%d).db"
   ```

3. **Límites de recursos:**
   ```bash
   # Limitar memoria
   ulimit -m 1048576  # 1GB
   ```

4. **Rotación de logs:**
   ```bash
   # Usar logrotate para archivos de log grandes
   sudo logrotate /etc/logrotate.d/leads-generator
   ```

Esta guía se actualiza regularmente. Para las últimas versiones, consulta la documentación oficial.