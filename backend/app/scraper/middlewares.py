"""
Middlewares avanzados de Scrapy para el proyecto de leads.
"""

import random
import time
import logging
import json
import uuid
from collections import deque
from scrapy.exceptions import NotConfigured
from scrapy import signals
from .settings import USER_AGENTS


class UserAgentRotationMiddleware:
    """Middleware avanzado para rotar User-Agents con estrategias inteligentes."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = logging.getLogger(__name__)

        # Configuración de user agents
        self.user_agents = crawler.settings.getlist('USER_AGENTS')
        if not self.user_agents:
            raise NotConfigured('USER_AGENTS is not configured')

        # Estrategias de rotación
        self.rotation_strategy = crawler.settings.get('USER_AGENT_ROTATION_STRATEGY', 'random')
        self.domain_user_agents = {}  # Cache de user agents por dominio
        self.request_count = 0

        # Configuración adicional
        self.min_requests_per_agent = crawler.settings.getint('MIN_REQUESTS_PER_AGENT', 5)
        self.max_requests_per_agent = crawler.settings.getint('MAX_REQUESTS_PER_AGENT', 20)

    @classmethod
    def from_crawler(cls, crawler):
        """Inicializa el middleware desde el crawler."""
        return cls(crawler)

    def process_request(self, request, spider):
        """Rota el User-Agent usando estrategia inteligente."""
        domain = self._get_domain(request.url)

        # Seleccionar estrategia de rotación
        if self.rotation_strategy == 'sticky':
            user_agent = self._get_sticky_user_agent(domain)
        elif self.rotation_strategy == 'weighted':
            user_agent = self._get_weighted_user_agent()
        elif self.rotation_strategy == 'adaptive':
            user_agent = self._get_adaptive_user_agent(domain)
        else:  # random (default)
            user_agent = self._get_random_user_agent()

        # Aplicar el user agent
        request.headers['User-Agent'] = user_agent
        request.meta['user_agent'] = user_agent  # Guardar para tracking

        self.request_count += 1
        self.logger.debug(f"🔄 Rotated User-Agent for {domain}: {user_agent}")

    def _get_random_user_agent(self):
        """Selecciona un user agent aleatorio."""
        return random.choice(self.user_agents)

    def _get_sticky_user_agent(self, domain):
        """Selecciona un user agent consistente por dominio."""
        if domain not in self.domain_user_agents:
            self.domain_user_agents[domain] = random.choice(self.user_agents)
        return self.domain_user_agents[domain]

    def _get_weighted_user_agent(self):
        """Selecciona un user agent con pesos (simula distribución real)."""
        # Los primeros user agents tienen más peso (son más comunes)
        weights = [0.4, 0.3, 0.15, 0.1, 0.05] + [0.01] * (len(self.user_agents) - 5)
        weights = weights[:len(self.user_agents)]

        return random.choices(self.user_agents, weights=weights, k=1)[0]

    def _get_adaptive_user_agent(self, domain):
        """Selecciona user agent adaptativo basado en el dominio y frecuencia."""
        # Cambiar user agent cada cierto número de requests por dominio
        domain_requests = self.domain_user_agents.get(domain, {'count': 0, 'agent': None})

        if domain_requests['count'] >= self.min_requests_per_agent:
            # Cambiar user agent
            new_agent = random.choice([ua for ua in self.user_agents if ua != domain_requests['agent']])
            self.domain_user_agents[domain] = {'count': 1, 'agent': new_agent}
            return new_agent
        else:
            # Mantener el mismo user agent
            if domain_requests['agent'] is None:
                domain_requests['agent'] = random.choice(self.user_agents)
            domain_requests['count'] += 1
            self.domain_user_agents[domain] = domain_requests
            return domain_requests['agent']

    def _get_domain(self, url):
        """Extrae el dominio de una URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc


class RateLimitingMiddleware:
    """Middleware para rate limiting avanzado por dominio con configuración específica."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = logging.getLogger(__name__)

        # Configuración de rate limiting
        self.min_delay = crawler.settings.getfloat('DOWNLOAD_DELAY', 1.0)
        self.max_delay = crawler.settings.getfloat('AUTOTHROTTLE_MAX_DELAY', 10.0)
        self.randomize_delay = crawler.settings.getbool('RANDOMIZE_DOWNLOAD_DELAY', True)

        # Configuración específica por dominio
        self.domain_delays = crawler.settings.getdict('DOMAIN_DELAYS', {})

        # Configuración de límites
        self.max_requests_per_domain = crawler.settings.getint('MAX_REQUESTS_PER_DOMAIN', 100)
        self.max_requests_per_session = crawler.settings.getint('MAX_REQUESTS_PER_SESSION', 1000)
        self.session_timeout = crawler.settings.getint('SESSION_TIMEOUT', 3600)

        # Tracking por dominio y sesión
        self.domain_last_request = {}
        self.domain_request_count = {}
        self.session_start_time = time.time()
        self.session_request_count = 0

        # Configuración de backoff exponencial
        self.backoff_base = crawler.settings.getfloat('RETRY_BACKOFF_BASE', 2.0)
        self.backoff_max_delay = crawler.settings.getint('RETRY_BACKOFF_MAX_DELAY', 300)

    @classmethod
    def from_crawler(cls, crawler):
        """Inicializa el middleware desde el crawler."""
        return cls(crawler)

    def process_request(self, request, spider):
        """Aplica rate limiting avanzado antes de cada request."""
        domain = self._get_domain(request.url)

        # Verificar límites de sesión
        if self._check_session_limits():
            self.logger.warning("🚫 Session limits reached, blocking request")
            return request  # Permitir que la solicitud continúe

        # Verificar límites por dominio
        if self._check_domain_limits(domain):
            self.logger.warning(f"🚫 Domain limits reached for {domain}, blocking request")
            return request  # Permitir que la solicitud continúe

        # Calcular delay necesario
        current_time = time.time()
        last_request_time = self.domain_last_request.get(domain, 0)
        time_since_last_request = current_time - last_request_time

        # Obtener delay específico del dominio o usar delay adaptativo
        domain_specific_delay = self.domain_delays.get(domain, self.min_delay)

        # Calcular delay adaptativo basado en la frecuencia de requests
        request_count = self.domain_request_count.get(domain, 0)
        adaptive_delay = min(domain_specific_delay * (1 + request_count * 0.05), self.max_delay)

        # Aplicar factor de aleatorización
        if self.randomize_delay:
            delay_factor = random.uniform(0.7, 1.3)  # Rango más conservador
            adaptive_delay *= delay_factor

        # Aplicar backoff exponencial si hay muchos requests al mismo dominio
        if request_count > 10:
            backoff_multiplier = min(self.backoff_base ** (request_count // 10), 5.0)
            adaptive_delay *= backoff_multiplier

        # Aplicar delay si es necesario
        if time_since_last_request < adaptive_delay:
            delay_needed = adaptive_delay - time_since_last_request
            self.logger.debug(".2f")
            time.sleep(delay_needed)

        # Actualizar tracking
        self.domain_last_request[domain] = time.time()
        self.domain_request_count[domain] = request_count + 1
        self.session_request_count += 1

        # Limpiar contadores antiguos (cada 50 requests por dominio)
        if request_count > 50:
            self.domain_request_count[domain] = 25  # Reset a la mitad

        # Loggear estadísticas cada 10 requests
        if self.session_request_count % 10 == 0:
            self._log_rate_limiting_stats()

    def _check_session_limits(self):
        """Verifica si se han alcanzado los límites de sesión."""
        # Verificar tiempo de sesión
        if time.time() - self.session_start_time > self.session_timeout:
            return True

        # Verificar número máximo de requests por sesión
        if self.session_request_count >= self.max_requests_per_session:
            return True

        return False

    def _check_domain_limits(self, domain):
        """Verifica si se han alcanzado los límites por dominio."""
        request_count = self.domain_request_count.get(domain, 0)
        return request_count >= self.max_requests_per_domain

    def _log_rate_limiting_stats(self):
        """Loggea estadísticas de rate limiting."""
        stats = {
            'session_requests': self.session_request_count,
            'domains_tracked': len(self.domain_request_count),
            'top_domains': sorted(self.domain_request_count.items(), key=lambda x: x[1], reverse=True)[:5]
        }
        self.logger.info(f"📊 Rate limiting stats: {stats}")

    def _get_domain(self, url):
        """Extrae el dominio de una URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc


class RequestFingerprintMiddleware:
    """Middleware para añadir fingerprints únicos a requests."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        """Inicializa el middleware desde el crawler."""
        return cls()

    def process_request(self, request, spider):
        """Añade headers adicionales para evitar detección."""
        # Headers para simular navegador real
        request.headers.setdefault('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        request.headers.setdefault('Accept-Language', 'en-US,en;q=0.5')
        request.headers.setdefault('Accept-Encoding', 'gzip, deflate')
        request.headers.setdefault('DNT', '1')
        request.headers.setdefault('Connection', 'keep-alive')
        request.headers.setdefault('Upgrade-Insecure-Requests', '1')

        # Añadir timestamp para requests únicos
        request.meta['request_timestamp'] = time.time()

        self.logger.debug(f"🛡️ Enhanced request fingerprint for: {request.url}")


class ErrorHandlingMiddleware:
    """Middleware para manejo avanzado y robusto de errores."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = logging.getLogger(__name__)

        # Configuración de reintentos
        self.max_retries = crawler.settings.getint('RETRY_TIMES', 3)
        self.retry_codes = crawler.settings.getlist('RETRY_HTTP_CODES', [500, 502, 503, 504, 408, 429])

        # Configuración de backoff
        self.backoff_base = crawler.settings.getfloat('RETRY_BACKOFF_BASE', 2.0)
        self.backoff_max_delay = crawler.settings.getint('RETRY_BACKOFF_MAX_DELAY', 300)

        # Configuración de detección de bloqueos
        self.blocked_patterns = crawler.settings.getlist('BLOCKED_PATTERNS', [
            'captcha', 'blocked', 'access denied', 'forbidden', 'rate limit',
            'too many requests', 'temporarily unavailable', 'service unavailable'
        ])

        # Tracking de errores por dominio
        self.domain_errors = {}
        self.domain_blocked_until = {}

        # Configuración de alertas
        self.alert_threshold = crawler.settings.getint('ERROR_ALERT_THRESHOLD', 5)
        self.alert_cooldown = crawler.settings.getint('ERROR_ALERT_COOLDOWN', 300)  # 5 minutos
        self.last_alert_time = 0

    @classmethod
    def from_crawler(cls, crawler):
        """Inicializa el middleware desde el crawler."""
        return cls(crawler)

    def process_response(self, request, response, spider):
        """Procesa la respuesta y decide si reintentar o manejar errores."""
        domain = self._get_domain(request.url)

        # Verificar si el dominio está bloqueado temporalmente
        if self._is_domain_blocked(domain):
            self.logger.warning(f"🚫 Domain {domain} is temporarily blocked, skipping request")
            return response  # Permitir que la respuesta continúe

        # Verificar códigos de error para reintento
        if response.status in self.retry_codes:
            return self._handle_retry(request, response, spider)

        # Verificar contenido de bloqueo/CAPTCHA
        if self._is_blocked_content(response):
            return self._handle_blocked_content(request, response, spider, domain)

        # Verificar errores específicos
        if response.status == 429:  # Too Many Requests
            return self._handle_rate_limit(request, response, spider, domain)
        elif response.status == 403:  # Forbidden
            return self._handle_forbidden(request, response, spider, domain)
        elif response.status >= 500:  # Server errors
            return self._handle_server_error(request, response, spider, domain)

        return response

    def process_exception(self, request, exception, spider):
        """Maneja excepciones durante el procesamiento de requests."""
        domain = self._get_domain(request.url)

        # Incrementar contador de errores para el dominio
        self._increment_domain_error(domain)

        # Loggear la excepción
        self.logger.error(f"❌ Exception in request to {request.url}: {str(exception)}")

        # Verificar si es un error temporal
        if self._is_temporary_error(exception):
            retries = request.meta.get('retry_times', 0)
            if retries < self.max_retries:
                return self._create_retry_request(request, retries + 1, f"Exception: {str(exception)}")

        # Verificar si es un error de conexión
        if self._is_connection_error(exception):
            self.logger.warning(f"🔌 Connection error for {domain}, may be network issue")

        # Verificar si es un error de timeout
        if self._is_timeout_error(exception):
            self.logger.warning(f"⏰ Timeout error for {request.url}")

        return request

    def _handle_retry(self, request, response, spider):
        """Maneja reintentos con backoff exponencial."""
        retries = request.meta.get('retry_times', 0)

        if retries < self.max_retries:
            self.logger.warning(f"⚠️ Retrying request to {request.url} (attempt {retries + 1}/{self.max_retries + 1}) - Status: {response.status}")

            # Calcular delay con backoff exponencial
            retry_delay = min(self.backoff_base ** retries, self.backoff_max_delay)
            request.meta['retry_times'] = retries + 1
            request.meta['download_delay'] = retry_delay

            # Crear nuevo request con headers ligeramente modificados
            new_request = self._create_retry_request(request, retries + 1, f"HTTP {response.status}")
            return new_request
        else:
            self.logger.error(f"❌ Max retries reached for {request.url} - Status: {response.status}")
            return response

    def _handle_blocked_content(self, request, response, spider, domain):
        """Maneja contenido que indica bloqueo."""
        self.logger.warning(f"🚫 Blocked content detected for {domain}")

        # Bloquear el dominio temporalmente
        self._block_domain_temporarily(domain, 300)  # 5 minutos

        # Enviar alerta si es necesario
        self._send_alert_if_needed(f"Blocked content detected for domain {domain}")

        return response

    def _handle_rate_limit(self, request, response, spider, domain):
        """Maneja rate limiting específico."""
        self.logger.warning(f"🚦 Rate limit detected for {domain}")

        # Bloquear dominio por más tiempo
        self._block_domain_temporarily(domain, 600)  # 10 minutos

        # Enviar alerta
        self._send_alert_if_needed(f"Rate limit exceeded for domain {domain}")

        return response

    def _handle_forbidden(self, request, response, spider, domain):
        """Maneja respuestas 403 Forbidden."""
        self.logger.warning(f"🚫 Forbidden access to {domain}")

        # Bloquear dominio por tiempo prolongado
        self._block_domain_temporarily(domain, 1800)  # 30 minutos

        # Enviar alerta
        self._send_alert_if_needed(f"Forbidden access to domain {domain}")

        return response

    def _handle_server_error(self, request, response, spider, domain):
        """Maneja errores del servidor."""
        retries = request.meta.get('retry_times', 0)

        if retries < self.max_retries:
            self.logger.warning(f"🛠️ Server error for {domain}, retrying...")
            return self._create_retry_request(request, retries + 1, f"Server error {response.status}")
        else:
            self.logger.error(f"❌ Persistent server error for {domain}")
            return response

    def _create_retry_request(self, original_request, retry_count, reason):
        """Crea un nuevo request para reintento."""
        from scrapy import Request

        # Modificar headers ligeramente para evitar detección
        new_headers = original_request.headers.copy()
        if 'User-Agent' in new_headers:
            # Cambiar ligeramente el user agent para reintentos
            ua = new_headers['User-Agent']
            if 'Chrome' in ua:
                new_headers['User-Agent'] = ua.replace('Chrome', 'Chromium')

        new_request = Request(
            url=original_request.url,
            callback=original_request.callback,
            meta=original_request.meta.copy(),
            headers=new_headers,
            dont_filter=True,
            errback=original_request.errback
        )

        # Añadir información de reintento
        new_request.meta['retry_times'] = retry_count
        new_request.meta['retry_reason'] = reason

        return new_request

    def _is_blocked_content(self, response):
        """Verifica si el contenido indica bloqueo."""
        if not hasattr(response, 'text'):
            return False

        content_lower = response.text.lower()
        return any(pattern.lower() in content_lower for pattern in self.blocked_patterns)

    def _is_domain_blocked(self, domain):
        """Verifica si un dominio está bloqueado temporalmente."""
        blocked_until = self.domain_blocked_until.get(domain, 0)
        return time.time() < blocked_until

    def _block_domain_temporarily(self, domain, duration_seconds):
        """Bloquea un dominio temporalmente."""
        blocked_until = time.time() + duration_seconds
        self.domain_blocked_until[domain] = blocked_until
        self.logger.warning(f"🚫 Domain {domain} blocked until {time.ctime(blocked_until)}")

    def _increment_domain_error(self, domain):
        """Incrementa el contador de errores para un dominio."""
        current_errors = self.domain_errors.get(domain, 0)
        self.domain_errors[domain] = current_errors + 1

    def _send_alert_if_needed(self, message):
        """Envía alerta si se supera el umbral."""
        current_time = time.time()

        # Verificar cooldown de alertas
        if current_time - self.last_alert_time < self.alert_cooldown:
            return

        # Contar errores totales recientes
        total_recent_errors = sum(self.domain_errors.values())

        if total_recent_errors >= self.alert_threshold:
            self.logger.error(f"🚨 ALERT: {message} (Total recent errors: {total_recent_errors})")
            self.last_alert_time = current_time

            # Aquí se podría integrar con sistemas de notificación externos
            # (email, Slack, Telegram, etc.)

    def _is_temporary_error(self, exception):
        """Verifica si una excepción es temporal."""
        temporary_errors = (
            'ConnectionError',
            'TimeoutError',
            'ConnectTimeout',
            'ReadTimeout',
            'ConnectionResetError',
            'ConnectionAbortedError'
        )
        return any(error_type in str(type(exception)) for error_type in temporary_errors)

    def _is_connection_error(self, exception):
        """Verifica si es un error de conexión."""
        connection_errors = (
            'ConnectionError',
            'ConnectionResetError',
            'ConnectionAbortedError',
            'ConnectionRefusedError'
        )
        return any(error_type in str(type(exception)) for error_type in connection_errors)

    def _is_timeout_error(self, exception):
        """Verifica si es un error de timeout."""
        timeout_errors = ('TimeoutError', 'ConnectTimeout', 'ReadTimeout')
        return any(error_type in str(type(exception)) for error_type in timeout_errors)

    def _get_domain(self, url):
        """Extrae el dominio de una URL."""
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.netloc


class DatabaseLoggingHandler(logging.Handler):
    """Handler personalizado para guardar logs en la base de datos."""

    def __init__(self, crawler):
        super().__init__()
        self.crawler = crawler
        self.session_id = str(uuid.uuid4())
        self.log_buffer = deque(maxlen=crawler.settings.getint('DB_LOG_BATCH_SIZE', 10))
        self.min_level = getattr(logging, crawler.settings.get('DB_LOG_LEVEL', 'WARNING'))

        # Crear sesión de scraping
        self._create_scraping_session()

    def _create_scraping_session(self):
        """Crea una nueva sesión de scraping en la base de datos."""
        try:
            from app.database.database import engine
            from app.database.models import ScrapingSession
            from sqlalchemy.orm import sessionmaker

            Session = sessionmaker(bind=engine)
            session = Session()

            scraping_session = ScrapingSession(
                session_id=self.session_id,
                start_url=self.crawler.spider.start_url if hasattr(self.crawler.spider, 'start_url') else 'unknown',
                max_depth=self.crawler.settings.getint('DEPTH_LIMIT', 3),
                allowed_domains=json.dumps(self.crawler.spider.allowed_domains) if hasattr(self.crawler.spider, 'allowed_domains') else None,
                user_agent=self.crawler.settings.get('USER_AGENT'),
                delay=self.crawler.settings.getfloat('DOWNLOAD_DELAY', 1.0)
            )

            session.add(scraping_session)
            session.commit()
            session.close()

        except Exception as e:
            logging.error(f"Error creating scraping session: {e}")

    def emit(self, record):
        """Procesa un registro de log."""
        if record.levelno < self.min_level:
            return

        # Crear entrada de log
        log_entry = {
            'session_id': self.session_id,
            'url': getattr(record, 'url', ''),
            'level': record.levelname,
            'message': record.getMessage(),
            'category': getattr(record, 'category', 'general'),
            'metadata': json.dumps(getattr(record, 'metadata', {}))
        }

        self.log_buffer.append(log_entry)

        # Guardar en lote si el buffer está lleno
        if len(self.log_buffer) >= self.log_buffer.maxlen:
            self._flush_logs()

    def _flush_logs(self):
        """Guarda los logs acumulados en la base de datos."""
        if not self.log_buffer:
            return

        try:
            from app.database.database import engine
            from app.database.models import ScrapingLog
            from sqlalchemy.orm import sessionmaker

            Session = sessionmaker(bind=engine)
            session = Session()

            for log_entry in self.log_buffer:
                log = ScrapingLog(**log_entry)
                session.add(log)

            session.commit()
            session.close()
            self.log_buffer.clear()

        except Exception as e:
            logging.error(f"Error saving logs to database: {e}")

    def close(self):
        """Cierra el handler y guarda los logs restantes."""
        self._flush_logs()
        super().close()


class MonitoringMiddleware:
    """Middleware para monitoreo avanzado del proceso de scraping."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = logging.getLogger(__name__)

        # Configurar logging a base de datos
        if crawler.settings.getbool('DB_LOG_ENABLED', True):
            db_handler = DatabaseLoggingHandler(crawler)
            logging.getLogger().addHandler(db_handler)
            self.db_handler = db_handler
        else:
            self.db_handler = None

    @classmethod
    def from_crawler(cls, crawler):
        """Inicializa el middleware desde el crawler."""
        return cls(crawler)

    def process_spider_open(self, spider):
        """Se ejecuta cuando el spider se abre."""
        self.logger.info("🕷️ Spider opened", extra={
            'category': 'spider',
            'metadata': {
                'spider_name': spider.name,
                'start_url': getattr(spider, 'start_url', 'unknown'),
                'allowed_domains': getattr(spider, 'allowed_domains', [])
            }
        })

    def process_spider_close(self, spider, reason):
        """Se ejecuta cuando el spider se cierra."""
        self.logger.info("🕷️ Spider closed", extra={
            'category': 'spider',
            'metadata': {
                'reason': reason,
                'stats': dict(spider.crawler.stats.get_stats())
            }
        })

        # Cerrar handler de base de datos
        if self.db_handler:
            self.db_handler.close()

    def process_request(self, request, spider):
        """Monitorea cada request."""
        # Añadir timestamp al request para medir tiempo de respuesta
        request.meta['request_start_time'] = time.time()

        self.logger.debug(f"📤 Request started: {request.url}", extra={
            'category': 'request',
            'url': request.url,
            'metadata': {
                'method': request.method,
                'headers_count': len(request.headers)
            }
        })

    def process_response(self, request, response, spider):
        """Monitorea cada respuesta."""
        # Calcular tiempo de respuesta
        start_time = request.meta.get('request_start_time')
        if start_time:
            response_time = (time.time() - start_time) * 1000  # en ms
        else:
            response_time = 0

        # Loggear respuesta
        if response.status >= 400:
            level = logging.WARNING
        else:
            level = logging.DEBUG

        self.logger.log(level, f"📥 Response received: {response.url}", extra={
            'category': 'response',
            'url': response.url,
            'metadata': {
                'status': response.status,
                'response_time': response_time,
                'content_length': len(response.body)
            }
        })

        return response