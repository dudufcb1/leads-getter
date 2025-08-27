"""
Configuración de Scrapy para el proyecto de leads.
"""

# Configuración básica
BOT_NAME = 'leads_generator'
SPIDER_MODULES = ['app.scraper.spiders']
NEWSPIDER_MODULE = 'app.scraper.spiders'

# Obediencia a robots.txt
ROBOTSTXT_OBEY = True

# Configuración avanzada de delays y concurrencia
DOWNLOAD_DELAY = 1.5  # Delay base reducido para mayor eficiencia
RANDOMIZE_DOWNLOAD_DELAY = True
DOWNLOAD_DELAY_RANDOM_FACTOR = 0.3  # Factor de aleatorización reducido (±30%)

# Límites de concurrencia optimizados
CONCURRENT_REQUESTS = 12  # Aumentado para mejor rendimiento
CONCURRENT_REQUESTS_PER_DOMAIN = 3  # Máximo por dominio (más conservador)
CONCURRENT_ITEMS = 200  # Mayor capacidad de procesamiento

# Configuración de profundidad avanzada
DEPTH_LIMIT = 4  # Profundidad máxima optimizada
DEPTH_STATS_VERBOSE = True
DEPTH_PRIORITY = 1  # Prioridad para requests de mayor profundidad

# Configuración de rate limiting avanzado y adaptativo
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.5  # Inicio más rápido
AUTOTHROTTLE_MAX_DELAY = 15.0  # Máximo delay aumentado
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.5  # Concurrencia objetivo optimizada
AUTOTHROTTLE_DEBUG = False
AUTOTHROTTLE_FEED_ENABLED = True  # Habilitar feed de información

# Configuración específica por dominio (rate limiting personalizado)
DOMAIN_DELAYS = {
    'google.com': 3.0,
    'facebook.com': 2.5,
    'twitter.com': 2.0,
    'linkedin.com': 2.5,
    'instagram.com': 2.0,
    'youtube.com': 1.5,
    'amazon.com': 2.0,
    'wikipedia.org': 1.0,
    'github.com': 1.5,
    'stackoverflow.com': 1.5,
}

# Configuración de cortesía adicional
COOKIES_ENABLED = True
TELNETCONSOLE_ENABLED = False
LOGSTATS_ENABLED = True

# Configuración de memoria y rendimiento
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 512  # Límite de memoria en MB
MEMUSAGE_WARNING_MB = 256  # Warning de memoria
MEMUSAGE_CHECK_INTERVAL_SECONDS = 60

# Configuración de pool de conexiones
REACTOR_THREADPOOL_MAXSIZE = 20  # Tamaño máximo del pool de hilos
DNSCACHE_ENABLED = True
DNSCACHE_SIZE = 10000  # Cache DNS más grande

# Configuración de cortesía adicional
ROBOTSTXT_OBEY = True
COOKIES_ENABLED = True
TELNETCONSOLE_ENABLED = False

# User agents avanzados para rotación
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
]

# Pipelines avanzados
ITEM_PIPELINES = {
    'app.scraper.pipelines.ContentValidationPipeline': 50,
    'app.scraper.pipelines.LanguageFilterPipeline': 100,
    'app.scraper.pipelines.AdvancedDuplicatePipeline': 150,
    'app.scraper.pipelines.DuplicateFilterPipeline': 200,
    'app.scraper.pipelines.QualityFilterPipeline': 250,
    'app.scraper.pipelines.DatabasePipeline': 300,
    'app.scraper.pipelines.StatsPipeline': 400,
}

# Configuración avanzada de logging
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s [%(name)s] %(levelname)s: %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

# Logging adicional para debugging
LOGSTATS_ENABLED = True
LOGSTATS_INTERVAL = 60.0  # Intervalo en segundos para estadísticas

# Configuración de logging a archivo
LOG_FILE_ENABLED = True
LOG_FILE_PATH = 'logs/scraping.log'
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10MB
LOG_FILE_BACKUP_COUNT = 5

# Configuración de logging a base de datos
DB_LOG_ENABLED = True
DB_LOG_LEVEL = 'WARNING'  # Solo logs de warning en adelante a BD
DB_LOG_BATCH_SIZE = 10  # Número de logs a guardar en lote

# Configuración de cache (opcional)
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 3600
HTTPCACHE_DIR = 'httpcache'

# Configuración avanzada de retries y timeouts
RETRY_ENABLED = True
RETRY_TIMES = 3
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]
RETRY_PRIORITY_ADJUST = -1  # Baja prioridad para reintentos

# Configuración de timeouts
DOWNLOAD_TIMEOUT = 30  # Timeout en segundos
DOWNLOAD_MAXSIZE = 10 * 1024 * 1024  # Máximo 10MB por página
DOWNLOAD_WARNSIZE = 5 * 1024 * 1024  # Warning a los 5MB

# Configuración de red
DNSCACHE_ENABLED = True
DNSCACHE_SIZE = 1000

# Configuración de redirects
REDIRECT_ENABLED = True
REDIRECT_MAX_TIMES = 20

# Configuración de cookies
COOKIES_ENABLED = True

# Configuración de middlewares avanzados
DOWNLOADER_MIDDLEWARES = {
    # Middlewares estándar de Scrapy
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
    'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 300,

    # Middlewares personalizados
    'app.scraper.middlewares.UserAgentRotationMiddleware': 400,
    'app.scraper.middlewares.RateLimitingMiddleware': 410,
    'app.scraper.middlewares.RequestFingerprintMiddleware': 420,
    'app.scraper.middlewares.ErrorHandlingMiddleware': 430,
    'app.scraper.middlewares.MonitoringMiddleware': 440,
}

# User agent personalizado (sin dependencia externa)
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Configuración de pipelines avanzados
ALLOWED_LANGUAGES = ['es', 'en', 'ca', 'pt']  # Idiomas permitidos
MIN_EMAILS_PER_PAGE = 0  # Mínimo de emails por página
MAX_EMAILS_PER_PAGE = 20  # Máximo de emails por página
MIN_CONTENT_LENGTH = 200  # Longitud mínima de contenido

# Configuración avanzada de límites y cortesía
MAX_REQUESTS_PER_DOMAIN = 100  # Máximo de requests por dominio por sesión
MAX_REQUESTS_PER_SESSION = 1000  # Máximo de requests por sesión completa
SESSION_TIMEOUT = 3600  # Timeout de sesión en segundos (1 hora)

# Configuración de backoff exponencial para reintentos
RETRY_BACKOFF_BASE = 2.0  # Base para backoff exponencial
RETRY_BACKOFF_MAX_DELAY = 300  # Máximo delay entre reintentos (5 minutos)

# Configuración de calidad de contenido
MIN_TITLE_LENGTH = 10  # Longitud mínima del título
MAX_TITLE_LENGTH = 200  # Longitud máxima del título
MIN_DESCRIPTION_LENGTH = 50  # Longitud mínima de descripción
MAX_DESCRIPTION_LENGTH = 500  # Longitud máxima de descripción

# Configuración de detección de idioma avanzada
LANGUAGE_CONFIDENCE_THRESHOLD = 0.7  # Umbral de confianza para detección de idioma
LANGUAGE_SAMPLE_SIZE = 1000  # Tamaño de muestra para detección de idioma

# Configuración de filtrado de URLs
MAX_URL_LENGTH = 2048  # Longitud máxima de URL
MIN_URL_LENGTH = 10  # Longitud mínima de URL
BLOCKED_URL_PATTERNS = [
    r'\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar|exe|dmg|deb|rpm)$',
    r'mailto:',
    r'javascript:',
    r'tel:',
    r'fax:',
    r'skype:',
    r'whatsapp:',
    r'telegram:',
    r'#',
    r'\bwp-admin\b',
    r'\bwp-login\b',
    r'\badmin\b',
    r'\blogin\b',
    r'\bauth\b',
    r'\bsignin\b',
    r'\bsignup\b',
    r'\bregister\b',
    r'\bpassword\b',
    r'\breset\b',
    r'\bverification\b',
    r'\bcaptcha\b',
    r'\brobot\b',
    r'\bbot\b',
    r'\bspam\b',
    r'\btest\b',
    r'\bdemo\b',
    r'\bexample\b',
    r'\bsample\b',
    r'\bplaceholder\b',
    r'\btemplate\b',
    r'\bdefault\b',
    r'\bnull\b',
    r'\bundefined\b',
    r'\bnone\b',
    r'\bempty\b',
    r'\bblank\b',
    r'\bna\b',
    r'\bn/a\b',
    r'\bnot\s+available\b',
    r'\bcoming\s+soon\b',
    r'\bunder\s+construction\b',
    r'\bmaintenance\b',
    r'\bout\s+of\s+service\b',
    r'\btemporarily\s+unavailable\b',
    r'\bservice\s+unavailable\b',
    r'\bsite\s+down\b',
    r'\bserver\s+error\b',
    r'\berror\s+page\b',
    r'\b404\b',
    r'\b403\b',
    r'\b500\b',
    r'\b502\b',
    r'\b503\b',
    r'\b504\b',
]

# Configuración de calidad de emails
EMAIL_QUALITY_WEIGHTS = {
    'has_name': 0.3,  # Email tiene nombre antes de @
    'has_domain': 0.4,  # Dominio válido
    'no_numbers': 0.1,  # No tiene números consecutivos
    'no_underscores': 0.1,  # No tiene underscores consecutivos
    'reasonable_length': 0.1,  # Longitud razonable
}

# Configuración de scoring de calidad de página
PAGE_QUALITY_WEIGHTS = {
    'has_title': 0.2,
    'has_description': 0.15,
    'has_keywords': 0.1,
    'content_length': 0.2,
    'has_emails': 0.15,
    'has_contact_info': 0.1,
    'load_speed': 0.1,
}

# Configuración de límites de recursos
MAX_MEMORY_USAGE_MB = 1024  # Máximo uso de memoria
MAX_CPU_USAGE_PERCENT = 80  # Máximo uso de CPU
MAX_DISK_USAGE_MB = 5000  # Máximo uso de disco para logs/cache

# Configuración de monitoreo
MONITORING_ENABLED = True
MONITORING_INTERVAL = 30  # Intervalo de monitoreo en segundos
MONITORING_METRICS = [
    'requests_count',
    'responses_count',
    'errors_count',
    'avg_response_time',
    'memory_usage',
    'cpu_usage',
    'disk_usage',
    'active_threads',
    'queue_size',
]

# Configuración de alertas
ALERT_EMAILS = []  # Lista de emails para alertas
ALERT_THRESHOLDS = {
    'error_rate': 0.1,  # 10% de tasa de error
    'memory_usage': 0.8,  # 80% de uso de memoria
    'cpu_usage': 0.9,  # 90% de uso de CPU
    'response_time': 10.0,  # 10 segundos promedio
}

# Configuración de exportación de datos
EXPORT_FORMATS = ['json', 'csv', 'xml', 'xlsx']
EXPORT_CHUNK_SIZE = 1000  # Tamaño de chunk para exportación
EXPORT_COMPRESSION = True  # Comprimir archivos exportados

# Configuración de backup
BACKUP_ENABLED = True
BACKUP_INTERVAL_HOURS = 24  # Intervalo de backup en horas
BACKUP_RETENTION_DAYS = 30  # Retención de backups en días
BACKUP_COMPRESSION = True  # Comprimir backups

# Configuración avanzada de filtrado de spam
SPAM_DOMAINS = [
    'example.com', 'test.com', 'spam.com', 'fake.com', 'tempmail.org',
    '10minutemail.com', 'guerrillamail.com', 'mailinator.com', 'yopmail.com',
    'throwaway.email', 'getnada.com', 'maildrop.cc', 'temp-mail.org',
    'mail-temporaire.fr', 'mytemp.email', 'mailcatch.com', 'fixmail.tk',
    'objectmail.com', 'proxymail.eu', 'rcpt.at', 'upliftnow.com',
    'uplipht.com', 'guerrillamail.biz', 'sharklasers.com', 'pokemail.net',
    'lifebyfood.com', 'chacuo.net', 'mailinator.gq', 'mailinator.ml'
]

SPAM_URL_PATTERNS = [
    r'/spam/', r'/test/', r'/fake/', r'/demo/', r'/sample/',
    r'/admin/', r'/login/', r'/register/', r'/password/',
    r'/captcha/', r'/robot/', r'/bot/', r'/verification/',
    r'/wp-admin/', r'/wp-login/', r'/administrator/', r'/admincp/',
    r'/backend/', r'/controlpanel/', r'/dashboard/', r'/manage/',
    r'/config/', r'/settings/', r'/preferences/', r'/account/',
    r'/profile/', r'/user/', r'/member/', r'/client/', r'/customer/'
]

# Configuración de palabras clave de negocio
BUSINESS_KEYWORDS = [
    'empresa', 'compañía', 'servicio', 'producto', 'contacto', 'teléfono',
    'dirección', 'email', 'sitio web', 'negocio', 'cliente', 'venta',
    'company', 'business', 'service', 'product', 'contact', 'phone',
    'address', 'website', 'client', 'customer', 'sale', 'marketing',
    'consultoría', 'consulting', 'desarrollo', 'development', 'proyecto',
    'project', 'solución', 'solution', 'soporte', 'support', 'equipo', 'team'
]

# Configuración de calidad de página avanzada
MIN_QUALITY_SCORE = 30  # Puntuación mínima de calidad de página
MIN_EMAILS_PER_PAGE = 0  # Mínimo de emails por página
MAX_EMAILS_PER_PAGE = 20  # Máximo de emails por página
MIN_CONTENT_LENGTH = 200  # Longitud mínima de contenido

# Configuración de duplicados avanzados
DUPLICATE_SIMILARITY_THRESHOLD = 0.85  # Umbral de similitud para detectar duplicados

FINGERPRINT_WEIGHTS = {
    'title': 0.4,  # Peso del título en el fingerprint
    'description': 0.3,  # Peso de la descripción
    'emails': 0.2,  # Peso de los emails
    'domain': 0.1,  # Peso del dominio
}

# Configuración de calidad de emails avanzada
EMAIL_QUALITY_WEIGHTS = {
    'has_name': 0.3,  # Email tiene nombre antes de @
    'has_domain': 0.4,  # Dominio válido
    'no_numbers': 0.1,  # No tiene números consecutivos
    'no_underscores': 0.1,  # No tiene underscores consecutivos
    'reasonable_length': 0.1,  # Longitud razonable
}

# Configuración de scoring de calidad de página
PAGE_QUALITY_WEIGHTS = {
    'has_title': 0.2,
    'has_description': 0.15,
    'has_keywords': 0.1,
    'content_length': 0.2,
    'has_emails': 0.15,
    'has_contact_info': 0.1,
    'load_speed': 0.1,
}

# Configuración de tipos de contenido
CONTENT_TYPES = {
    'business': ['empresa', 'compañía', 'negocio', 'company', 'business'],
    'blog': ['blog', 'noticia', 'artículo', 'news', 'article', 'post'],
    'landing': ['landing', 'inicio', 'home', 'principal', 'main'],
    'contact': ['contacto', 'contact', 'teléfono', 'phone', 'dirección'],
    'portfolio': ['portafolio', 'portfolio', 'proyecto', 'project', 'trabajo'],
    'about': ['acerca', 'about', 'nosotros', 'team', 'equipo'],
    'services': ['servicios', 'services', 'productos', 'products'],
    'unknown': []
}

# Configuración de validación de contenido
MIN_TITLE_LENGTH = 10  # Longitud mínima del título
MAX_TITLE_LENGTH = 200  # Longitud máxima del título
MIN_DESCRIPTION_LENGTH = 50  # Longitud mínima de descripción
MAX_DESCRIPTION_LENGTH = 500  # Longitud máxima de descripción

# Configuración de logging avanzado
LOG_REQUEST_DETAILS = True  # Log detallado de requests
LOG_RESPONSE_DETAILS = False  # Log detallado de responses (puede ser verbose)
LOG_ITEM_DETAILS = True  # Log detallado de items procesados
LOG_FILTERED_ITEMS = True  # Log de items filtrados

# Configuración de métricas de rendimiento
PERFORMANCE_METRICS_ENABLED = True
PERFORMANCE_LOG_INTERVAL = 100  # Log cada 100 items
PERFORMANCE_WARNING_THRESHOLDS = {
    'avg_response_time': 5.0,  # Warning si promedio > 5 segundos
    'error_rate': 0.05,  # Warning si tasa de error > 5%
    'memory_usage_mb': 400,  # Warning si memoria > 400MB
    'cpu_usage_percent': 70,  # Warning si CPU > 70%
}