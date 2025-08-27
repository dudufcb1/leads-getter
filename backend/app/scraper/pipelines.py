"""
Pipelines avanzados de Scrapy para procesar y guardar los items.
"""

from sqlalchemy.orm import sessionmaker
import sys
import os
import re
import hashlib
import logging
from collections import defaultdict
from typing import Set, Dict, List
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.database.database import engine
from app.database.models import Website, Email


class DatabasePipeline:
    """Pipeline para guardar items en la base de datos."""

    def __init__(self):
        """Inicializa la sesión de base de datos."""
        # Importar y crear las tablas si no existen
        from app.database.models import Base
        Base.metadata.create_all(bind=engine)
        self.Session = sessionmaker(bind=engine)

    def process_item(self, item, spider):
        """Procesa un item y lo guarda en la base de datos."""
        spider.logger.info(f"🗄️ Pipeline processing item: {item}")
        session = self.Session()

        try:
            # Crear o actualizar el sitio web
            website = session.query(Website).filter_by(url=item['url']).first()

            if not website:
                spider.logger.info(f"🆕 Creating new website entry for: {item['url']}")
                website = Website(
                    url=item['url'],
                    domain=item['domain'],
                    language=item.get('language'),
                    status=item.get('status', 'processed'),
                    depth_level=item.get('depth_level', 0),
                    source_url=item.get('source_url'),

                    # Campos avanzados de calidad
                    page_quality_score=item.get('page_quality_score', 0),
                    email_quality_score=item.get('email_quality_score', 0.0),
                    contact_score=item.get('contact_score', 0),
                    content_type=item.get('content_type'),
                    has_business_keywords=','.join(item.get('has_business_keywords', [])) if item.get('has_business_keywords') else None,

                    # Campos de validación
                    is_spam=item.get('is_spam', 0),
                    language_confidence=item.get('language_confidence', 0.0),
                    duplicate_hash=item.get('duplicate_hash'),
                    fingerprint=item.get('fingerprint'),

                    # Campos de rendimiento
                    load_time=item.get('load_time'),
                    word_count=item.get('word_count', 0),
                    link_count=item.get('link_count', 0),
                    image_count=item.get('image_count', 0),

                    # Metadata adicional
                    title=item.get('title'),
                    description=item.get('description'),
                    keywords=item.get('keywords'),

                    # Campos existentes
                    response_time=item.get('response_time'),
                    page_size=item.get('page_size'),
                    http_status=item.get('http_status'),
                    quality_score=item.get('quality_score', 0),
                    email_count=len(item.get('emails', [])),
                    last_scraped=item.get('scraped_at'),
                    user_agent=item.get('user_agent'),
                    ip_address=item.get('ip_address')
                )
                session.add(website)
                session.flush()  # Para obtener el ID
                spider.logger.info(f"✅ Website created with ID: {website.id}")
            else:
                spider.logger.info(f"🔍 Found existing website: {website.id}")
                # Actualizar campos si es necesario
                website.page_quality_score = item.get('page_quality_score', website.page_quality_score)
                website.email_quality_score = item.get('email_quality_score', website.email_quality_score)
                website.contact_score = item.get('contact_score', website.contact_score)
                website.content_type = item.get('content_type', website.content_type)
                website.has_business_keywords = ','.join(item.get('has_business_keywords', [])) if item.get('has_business_keywords') else website.has_business_keywords
                website.is_spam = item.get('is_spam', website.is_spam)
                website.language_confidence = item.get('language_confidence', website.language_confidence)
                website.duplicate_hash = item.get('duplicate_hash', website.duplicate_hash)
                website.fingerprint = item.get('fingerprint', website.fingerprint)
                website.load_time = item.get('load_time', website.load_time)
                website.word_count = item.get('word_count', website.word_count)
                website.link_count = item.get('link_count', website.link_count)
                website.image_count = item.get('image_count', website.image_count)
                website.title = item.get('title', website.title)
                website.description = item.get('description', website.description)
                website.keywords = item.get('keywords', website.keywords)
                website.email_count = len(item.get('emails', []))
                website.last_scraped = item.get('scraped_at', website.last_scraped)
                website.scrape_count += 1

            # Guardar emails encontrados
            emails = item.get('emails', [])
            for email_addr in emails:
                # Verificar si el email ya existe para este sitio
                existing_email = session.query(Email).filter_by(
                    website_id=website.id,
                    email=email_addr
                ).first()

                if not existing_email:
                    # Calcular calidad del email
                    email_quality = self._calculate_email_quality(email_addr, item)

                    email_item = Email(
                        website_id=website.id,
                        email=email_addr,
                        source_page=item['url'],
                        quality_score=email_quality,
                        context=item.get('email_context', {}).get(email_addr),
                        anchor_text=item.get('email_anchors', {}).get(email_addr)
                    )
                    session.add(email_item)

            session.commit()
            spider.logger.info(f"💾 Successfully saved item to database")

        except Exception as e:
            session.rollback()
            spider.logger.error(f"Error saving item to database: {e}")
        finally:
            session.close()

        return item

    def _calculate_email_quality(self, email, item):
        """Calcula la calidad de un email específico."""
        score = 50  # Base score

        # Verificar formato básico
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return 10

        # Penalizaciones por dominios spam
        spam_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com']
        domain = email.split('@')[1] if '@' in email else ''
        if domain in spam_domains:
            score -= 20

        # Bonus por dominios corporativos
        if '.' in domain and len(domain.split('.')[-1]) > 2:
            corporate_indicators = ['.com', '.org', '.net', '.biz', '.info']
            if any(indicator in domain for indicator in corporate_indicators):
                score += 10

        # Bonus por contexto de calidad
        if item.get('content_type') in ['business', 'contact', 'about']:
            score += 15

        # Bonus por palabras clave de negocio
        business_keywords = item.get('has_business_keywords', [])
        if business_keywords:
            score += min(len(business_keywords) * 5, 20)

        return max(0, min(100, score))


class LanguageFilterPipeline:
    """Pipeline para filtrar contenido por idioma."""

    def __init__(self, allowed_languages=None):
        self.allowed_languages = allowed_languages or ['es', 'en']
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        """Inicializa el pipeline desde el crawler."""
        allowed_languages = crawler.settings.getlist('ALLOWED_LANGUAGES', ['es', 'en'])
        return cls(allowed_languages)

    def process_item(self, item, spider):
        """Filtra items basado en el idioma detectado."""
        item_language = item.get('language')

        if item_language and item_language not in self.allowed_languages:
            spider.logger.info(f"🌍 Filtering out item with language '{item_language}': {item.get('url')}")
            from scrapy.exceptions import DropItem
            raise DropItem(f"Language '{item_language}' not in allowed languages")

        return item


class DuplicateFilterPipeline:
    """Pipeline avanzado para filtrar duplicados basado en contenido y URLs."""

    def __init__(self):
        self.seen_urls: Set[str] = set()
        self.seen_content_hashes: Set[str] = set()
        self.seen_emails: Set[str] = set()
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_crawler(cls, crawler):
        """Inicializa el pipeline desde el crawler."""
        return cls()

    def process_item(self, item, spider):
        """Filtra items duplicados."""
        # Verificar URL duplicada
        url = item.get('url')
        if url in self.seen_urls:
            spider.logger.debug(f"🔄 Duplicate URL filtered: {url}")
            from scrapy.exceptions import DropItem
            raise DropItem(f"Duplicate URL: {url}")

        # Verificar contenido duplicado (hash del texto)
        content_hash = self._get_content_hash(item)
        if content_hash and content_hash in self.seen_content_hashes:
            spider.logger.debug(f"📄 Duplicate content filtered: {url}")
            from scrapy.exceptions import DropItem
            raise DropItem(f"Duplicate content: {url}")

        # Verificar emails duplicados
        emails = item.get('emails', [])
        duplicate_emails = []
        for email in emails:
            if email in self.seen_emails:
                duplicate_emails.append(email)

        if duplicate_emails:
            spider.logger.debug(f"📧 Duplicate emails filtered: {duplicate_emails}")
            # Remover emails duplicados pero mantener el item
            item['emails'] = [email for email in emails if email not in self.seen_emails]

        # Si no quedan emails después del filtrado, decidir si descartar el item
        if not item.get('emails') and emails:
            spider.logger.debug(f"🚫 No unique emails left, filtering item: {url}")
            from scrapy.exceptions import DropItem
            raise DropItem(f"No unique emails: {url}")

        # Registrar como visto
        self.seen_urls.add(url)
        if content_hash:
            self.seen_content_hashes.add(content_hash)
        for email in item.get('emails', []):
            self.seen_emails.add(email)

        return item

    def _get_content_hash(self, item):
        """Genera un hash del contenido para detectar duplicados."""
        # Crear una representación del contenido
        content_parts = [
            item.get('url', ''),
            item.get('domain', ''),
            str(item.get('emails', []))
        ]
        content = '|'.join(content_parts)

        if content:
            return hashlib.md5(content.encode('utf-8')).hexdigest()
        return None


class QualityFilterPipeline:
    """Pipeline avanzado para filtrar contenido basado en calidad y relevancia."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = logging.getLogger(__name__)

        # Configuración básica
        self.min_emails = crawler.settings.getint('MIN_EMAILS_PER_PAGE', 0)
        self.max_emails = crawler.settings.getint('MAX_EMAILS_PER_PAGE', 20)
        self.min_content_length = crawler.settings.getint('MIN_CONTENT_LENGTH', 200)

        # Configuración de calidad
        self.min_quality_score = crawler.settings.getint('MIN_QUALITY_SCORE', 30)
        self.language_confidence_threshold = crawler.settings.getfloat('LANGUAGE_CONFIDENCE_THRESHOLD', 0.7)

        # Lista negra de dominios spam
        self.spam_domains = crawler.settings.getlist('SPAM_DOMAINS', [
            'example.com', 'test.com', 'spam.com', 'fake.com', 'tempmail.org',
            '10minutemail.com', 'guerrillamail.com', 'mailinator.com', 'yopmail.com',
            'throwaway.email', 'getnada.com', 'maildrop.cc', 'temp-mail.org'
        ])

        # Patrones de spam en URLs
        self.spam_url_patterns = crawler.settings.getlist('SPAM_URL_PATTERNS', [
            r'/spam/', r'/test/', r'/fake/', r'/demo/', r'/sample/',
            r'/admin/', r'/login/', r'/register/', r'/password/',
            r'/captcha/', r'/robot/', r'/bot/', r'/verification/'
        ])

        # Configuración de emails
        self.email_quality_weights = crawler.settings.getdict('EMAIL_QUALITY_WEIGHTS', {
            'has_name': 0.3,
            'has_domain': 0.4,
            'no_numbers': 0.1,
            'no_underscores': 0.1,
            'reasonable_length': 0.1,
        })

        # Configuración de página
        self.page_quality_weights = crawler.settings.getdict('PAGE_QUALITY_WEIGHTS', {
            'has_title': 0.2,
            'has_description': 0.15,
            'has_keywords': 0.1,
            'content_length': 0.2,
            'has_emails': 0.15,
            'has_contact_info': 0.1,
            'load_speed': 0.1,
        })

    @classmethod
    def from_crawler(cls, crawler):
        """Inicializa el pipeline desde el crawler."""
        return cls(crawler)

    def process_item(self, item, spider):
        """Filtra items basado en criterios de calidad avanzados."""
        url = item.get('url', '')
        domain = item.get('domain', '')

        # Verificar dominio spam
        if self._is_spam_domain(domain):
            spider.logger.debug(f"🚫 Spam domain filtered: {domain}")
            from scrapy.exceptions import DropItem
            raise DropItem(f"Spam domain: {domain}")

        # Verificar patrones spam en URL
        if self._is_spam_url(url):
            spider.logger.debug(f"🚫 Spam URL pattern filtered: {url}")
            from scrapy.exceptions import DropItem
            raise DropItem(f"Spam URL pattern: {url}")

        # Calcular puntuación de calidad de página
        page_score = self._calculate_page_quality_score(item)
        item['page_quality_score'] = page_score

        if page_score < self.min_quality_score:
            spider.logger.debug(f"📊 Low quality page filtered (score: {page_score}): {url}")
            from scrapy.exceptions import DropItem
            raise DropItem(f"Low quality page: {page_score}")

        # Verificar emails
        emails = item.get('emails', [])
        if len(emails) < self.min_emails:
            spider.logger.debug(f"📧 Too few emails ({len(emails)} < {self.min_emails}): {url}")
            from scrapy.exceptions import DropItem
            raise DropItem(f"Too few emails: {len(emails)}")

        if len(emails) > self.max_emails:
            spider.logger.debug(f"📧 Too many emails ({len(emails)} > {self.max_emails}): {url}")
            from scrapy.exceptions import DropItem
            raise DropItem(f"Too many emails: {len(emails)}")

        # Filtrar y validar emails
        quality_emails = []
        for email in emails:
            if self._is_quality_email(email):
                quality_emails.append(email)

        if not quality_emails:
            spider.logger.debug(f"📧 No quality emails found: {url}")
            from scrapy.exceptions import DropItem
            raise DropItem("No quality emails")

        # Actualizar emails con los de calidad
        item['emails'] = quality_emails
        item['email_quality_score'] = len(quality_emails) / len(emails) if emails else 0

        # Verificar profundidad
        depth = item.get('depth_level', 0)
        max_depth = self.crawler.settings.getint('DEPTH_LIMIT', 5)
        if depth > max_depth:
            spider.logger.debug(f"🏊 Too deep ({depth} > {max_depth}): {url}")
            from scrapy.exceptions import DropItem
            raise DropItem(f"Too deep: {depth}")

        # Verificar idioma con confianza
        language = item.get('language', '')
        if language and not self._is_language_confident(item):
            spider.logger.debug(f"🌍 Low language confidence: {url}")
            from scrapy.exceptions import DropItem
            raise DropItem("Low language confidence")

        return item

    def _is_spam_domain(self, domain):
        """Verifica si el dominio está en la lista negra."""
        return domain.lower() in {d.lower() for d in self.spam_domains}

    def _is_spam_url(self, url):
        """Verifica si la URL contiene patrones spam."""
        for pattern in self.spam_url_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False

    def _calculate_page_quality_score(self, item):
        """Calcula una puntuación de calidad para la página."""
        score = 0

        # Puntuación por título
        if item.get('title') and len(item.get('title', '')) > 10:
            score += self.page_quality_weights['has_title'] * 100

        # Puntuación por descripción
        if item.get('description') and len(item.get('description', '')) > 50:
            score += self.page_quality_weights['has_description'] * 100

        # Puntuación por palabras clave
        if item.get('keywords'):
            score += self.page_quality_weights['has_keywords'] * 100

        # Puntuación por longitud de contenido
        content_length = len(item.get('url', ''))  # Aproximación
        if content_length > self.min_content_length:
            content_score = min(content_length / 1000, 1.0)  # Máximo 1.0
            score += self.page_quality_weights['content_length'] * 100 * content_score

        # Puntuación por emails
        emails = item.get('emails', [])
        if emails:
            email_score = min(len(emails) / 5, 1.0)  # Máximo 1.0 para 5+ emails
            score += self.page_quality_weights['has_emails'] * 100 * email_score

        # Puntuación por información de contacto
        has_contact_info = any(keyword in item.get('url', '').lower() for keyword in
                              ['contact', 'about', 'team', 'staff', 'nosotros'])
        if has_contact_info:
            score += self.page_quality_weights['has_contact_info'] * 100

        return int(score)

    def _is_quality_email(self, email):
        """Verifica si un email es de calidad usando múltiples criterios."""
        if not email or len(email) > 254:  # RFC 5321
            return False

        # Verificar formato básico
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False

        score = 0

        # Tiene nombre antes del @
        if '@' in email:
            local_part = email.split('@')[0]
            if len(local_part) > 2 and not local_part.isdigit():
                score += self.email_quality_weights['has_name']

        # Tiene dominio válido
        if '@' in email:
            domain_part = email.split('@')[1]
            if '.' in domain_part and len(domain_part) > 4:
                score += self.email_quality_weights['has_domain']

        # No tiene números consecutivos
        if not re.search(r'\d{3,}', email):
            score += self.email_quality_weights['no_numbers']

        # No tiene underscores consecutivos
        if not re.search(r'_+', email):
            score += self.email_quality_weights['no_underscores']

        # Longitud razonable
        if 5 <= len(email) <= 100:
            score += self.email_quality_weights['reasonable_length']

        # Evitar emails temporales o spam
        spam_patterns = [
            r'temp', r'spam', r'fake', r'test', r'example', r'sample',
            r'admin', r'root', r'noreply', r'do-not-reply', r'no-reply',
            r'system', r'mailer', r'daemon', r'postmaster', r'abuse',
            r'webmaster', r'hostmaster', r'info', r'support'
        ]

        for pattern in spam_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                score -= 0.5  # Penalización

        return score >= 0.6  # Umbral de calidad

    def _is_language_confident(self, item):
        """Verifica si la detección de idioma tiene suficiente confianza."""
        # Esta es una implementación básica
        # En producción se podría usar langdetect u otras librerías
        language = item.get('language', '')
        if not language:
            return True

        # Verificar si el idioma está en la lista permitida
        allowed_languages = self.crawler.settings.getlist('ALLOWED_LANGUAGES', ['es', 'en'])
        return language in allowed_languages


class ContentValidationPipeline:
    """Pipeline para validar y enriquecer el contenido de las páginas."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = logging.getLogger(__name__)

        # Configuración de validación
        self.min_title_length = crawler.settings.getint('MIN_TITLE_LENGTH', 10)
        self.max_title_length = crawler.settings.getint('MAX_TITLE_LENGTH', 200)
        self.min_description_length = crawler.settings.getint('MIN_DESCRIPTION_LENGTH', 50)
        self.max_description_length = crawler.settings.getint('MAX_DESCRIPTION_LENGTH', 500)

        # Palabras clave importantes por sector
        self.business_keywords = crawler.settings.getlist('BUSINESS_KEYWORDS', [
            'empresa', 'compañía', 'servicio', 'producto', 'contacto', 'teléfono',
            'dirección', 'email', 'sitio web', 'negocio', 'cliente', 'venta'
        ])

    @classmethod
    def from_crawler(cls, crawler):
        """Inicializa el pipeline desde el crawler."""
        return cls(crawler)

    def process_item(self, item, spider):
        """Valida y enriquece el contenido del item."""
        # Validar y limpiar título
        title = self._clean_title(item.get('title', ''))
        if title:
            item['title'] = title
        else:
            spider.logger.debug(f"📝 Invalid title: {item.get('url')}")

        # Validar y limpiar descripción
        description = self._clean_description(item.get('description', ''))
        if description:
            item['description'] = description

        # Extraer información adicional
        item['has_business_keywords'] = self._has_business_keywords(item)
        item['content_type'] = self._detect_content_type(item)
        item['contact_score'] = self._calculate_contact_score(item)

        return item

    def _clean_title(self, title):
        """Limpia y valida el título."""
        if not title:
            return None

        # Limpiar espacios extra
        title = re.sub(r'\s+', ' ', title.strip())

        # Verificar longitud
        if not (self.min_title_length <= len(title) <= self.max_title_length):
            return None

        # Evitar títulos spam
        spam_patterns = [
            r'^test', r'^demo', r'^sample', r'^untitled', r'^no title',
            r'^home', r'^index', r'^page', r'^welcome', r'^default'
        ]

        for pattern in spam_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                return None

        return title

    def _clean_description(self, description):
        """Limpia y valida la descripción."""
        if not description:
            return None

        # Limpiar espacios extra
        description = re.sub(r'\s+', ' ', description.strip())

        # Verificar longitud
        if not (self.min_description_length <= len(description) <= self.max_description_length):
            return None

        return description

    def _has_business_keywords(self, item):
        """Verifica si el contenido contiene palabras clave de negocio."""
        text_content = ' '.join([
            item.get('title', ''),
            item.get('description', ''),
            item.get('url', '')
        ]).lower()

        found_keywords = []
        for keyword in self.business_keywords:
            if keyword.lower() in text_content:
                found_keywords.append(keyword)

        return found_keywords

    def _detect_content_type(self, item):
        """Detecta el tipo de contenido de la página."""
        url = item.get('url', '').lower()
        title = item.get('title', '').lower()
        description = item.get('description', '').lower()

        # Patrones para diferentes tipos de contenido
        content_patterns = {
            'business': [
                r'empresa', r'compañía', r'negocio', r'servicio', r'producto',
                r'contacto', r'acerca', r'nosotros', r'about', r'company'
            ],
            'blog': [
                r'blog', r'noticia', r'artículo', r'post', r'news', r'article'
            ],
            'landing': [
                r'landing', r'inicio', r'home', r'principal', r'main'
            ],
            'contact': [
                r'contacto', r'contact', r'teléfono', r'phone', r'dirección'
            ],
            'portfolio': [
                r'portafolio', r'portfolio', r'proyecto', r'project', r'trabajo'
            ]
        }

        for content_type, patterns in content_patterns.items():
            for pattern in patterns:
                if (re.search(pattern, url) or
                    re.search(pattern, title) or
                    re.search(pattern, description)):
                    return content_type

        return 'unknown'

    def _calculate_contact_score(self, item):
        """Calcula una puntuación de información de contacto."""
        score = 0

        # Emails encontrados
        emails = item.get('emails', [])
        score += len(emails) * 10

        # Palabras clave de contacto
        contact_keywords = ['contacto', 'contact', 'teléfono', 'phone', 'dirección', 'address']
        text_content = ' '.join([
            item.get('title', ''),
            item.get('description', ''),
            item.get('url', '')
        ]).lower()

        for keyword in contact_keywords:
            if keyword in text_content:
                score += 5

        return min(score, 100)  # Máximo 100


class AdvancedDuplicatePipeline:
    """Pipeline avanzado para detectar duplicados usando fingerprints."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.logger = logging.getLogger(__name__)

        # Configuración
        self.similarity_threshold = crawler.settings.getfloat('DUPLICATE_SIMILARITY_THRESHOLD', 0.85)
        self.fingerprint_cache = {}
        self.url_cache = set()

        # Configuración de fingerprinting
        self.fingerprint_weights = crawler.settings.getdict('FINGERPRINT_WEIGHTS', {
            'title': 0.4,
            'description': 0.3,
            'emails': 0.2,
            'domain': 0.1,
        })

    @classmethod
    def from_crawler(cls, crawler):
        """Inicializa el pipeline desde el crawler."""
        return cls(crawler)

    def process_item(self, item, spider):
        """Detecta duplicados usando fingerprints avanzados."""
        url = item.get('url', '')

        # Verificar URL duplicada primero
        if url in self.url_cache:
            spider.logger.debug(f"🔄 Duplicate URL: {url}")
            from scrapy.exceptions import DropItem
            raise DropItem(f"Duplicate URL: {url}")

        # Generar fingerprint
        fingerprint = self._generate_fingerprint(item)

        # Verificar duplicados por fingerprint
        if fingerprint in self.fingerprint_cache:
            cached_item = self.fingerprint_cache[fingerprint]
            similarity = self._calculate_similarity(item, cached_item)

            if similarity >= self.similarity_threshold:
                spider.logger.debug(f"📄 Duplicate content (similarity: {similarity:.2f}): {url}")
                from scrapy.exceptions import DropItem
                raise DropItem(f"Duplicate content: {similarity:.2f}")

        # Registrar como visto
        self.url_cache.add(url)
        self.fingerprint_cache[fingerprint] = item

        return item

    def _generate_fingerprint(self, item):
        """Genera un fingerprint único para el item."""
        components = []

        # Componente de título
        title = item.get('title', '').lower().strip()
        if title:
            components.append(f"title:{hashlib.md5(title.encode()).hexdigest()[:8]}")

        # Componente de descripción
        description = item.get('description', '').lower().strip()
        if description:
            components.append(f"desc:{hashlib.md5(description.encode()).hexdigest()[:8]}")

        # Componente de emails
        emails = sorted(item.get('emails', []))
        if emails:
            email_hash = hashlib.md5('|'.join(emails).encode()).hexdigest()[:8]
            components.append(f"emails:{email_hash}")

        # Componente de dominio
        domain = item.get('domain', '')
        if domain:
            components.append(f"domain:{domain}")

        # Crear fingerprint final
        fingerprint = '|'.join(components)
        return hashlib.md5(fingerprint.encode()).hexdigest()

    def _calculate_similarity(self, item1, item2):
        """Calcula la similitud entre dos items."""
        similarity_scores = []

        # Similitud de título
        title1 = item1.get('title', '').lower()
        title2 = item2.get('title', '').lower()
        if title1 and title2:
            title_sim = self._text_similarity(title1, title2)
            similarity_scores.append(title_sim * self.fingerprint_weights['title'])

        # Similitud de descripción
        desc1 = item1.get('description', '').lower()
        desc2 = item2.get('description', '').lower()
        if desc1 and desc2:
            desc_sim = self._text_similarity(desc1, desc2)
            similarity_scores.append(desc_sim * self.fingerprint_weights['description'])

        # Similitud de emails
        emails1 = set(item1.get('emails', []))
        emails2 = set(item2.get('emails', []))
        if emails1 and emails2:
            email_sim = len(emails1.intersection(emails2)) / len(emails1.union(emails2))
            similarity_scores.append(email_sim * self.fingerprint_weights['emails'])

        # Similitud de dominio
        domain1 = item1.get('domain', '')
        domain2 = item2.get('domain', '')
        if domain1 and domain2:
            domain_sim = 1.0 if domain1 == domain2 else 0.0
            similarity_scores.append(domain_sim * self.fingerprint_weights['domain'])

        return sum(similarity_scores) / sum(self.fingerprint_weights.values()) if similarity_scores else 0

    def _text_similarity(self, text1, text2):
        """Calcula similitud de texto básica usando Jaccard."""
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 or not words2:
            return 0

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        return intersection / union if union > 0 else 0


class StatsPipeline:
    """Pipeline avanzado para recopilar estadísticas del proceso de scraping."""

    def __init__(self, crawler):
        self.crawler = crawler
        self.stats = defaultdict(int)
        self.logger = logging.getLogger(__name__)

        # Estadísticas adicionales
        self.quality_scores = []
        self.processing_times = []
        self.error_counts = defaultdict(int)

    @classmethod
    def from_crawler(cls, crawler):
        """Inicializa el pipeline desde el crawler."""
        return cls(crawler)

    def process_item(self, item, spider):
        """Recopila estadísticas avanzadas de los items procesados."""
        # Estadísticas básicas
        self.stats['items_processed'] += 1

        # Estadísticas por dominio
        domain = item.get('domain', 'unknown')
        self.stats[f'domain_{domain}'] += 1

        # Estadísticas de emails
        emails = item.get('emails', [])
        self.stats['total_emails'] += len(emails)

        if emails:
            self.stats['items_with_emails'] += 1
            self.stats['avg_emails_per_item'] = self.stats['total_emails'] / self.stats['items_processed']

        # Estadísticas por idioma
        language = item.get('language', 'unknown')
        self.stats[f'language_{language}'] += 1

        # Estadísticas por profundidad
        depth = item.get('depth_level', 0)
        self.stats[f'depth_{depth}'] += 1

        # Estadísticas de calidad
        quality_score = item.get('page_quality_score', 0)
        if quality_score > 0:
            self.quality_scores.append(quality_score)
            self.stats['avg_quality_score'] = sum(self.quality_scores) / len(self.quality_scores)

        # Estadísticas de tipo de contenido
        content_type = item.get('content_type', 'unknown')
        self.stats[f'content_type_{content_type}'] += 1

        # Estadísticas de contacto
        contact_score = item.get('contact_score', 0)
        if contact_score > 50:
            self.stats['high_contact_score_items'] += 1

        # Estadísticas de palabras clave de negocio
        business_keywords = item.get('has_business_keywords', [])
        if business_keywords:
            self.stats['items_with_business_keywords'] += 1

        # Log estadísticas cada 50 items
        if self.stats['items_processed'] % 50 == 0:
            self._log_stats(spider)

        return item

    def _log_stats(self, spider):
        """Registra las estadísticas actuales."""
        spider.logger.info("📊 Advanced Scraping Statistics:")
        spider.logger.info(f"   Items processed: {self.stats['items_processed']}")
        spider.logger.info(f"   Items with emails: {self.stats['items_with_emails']}")
        spider.logger.info(f"   Total emails: {self.stats['total_emails']}")
        spider.logger.info(".2f")
        spider.logger.info(".1f")
        spider.logger.info(f"   High contact score items: {self.stats.get('high_contact_score_items', 0)}")
        spider.logger.info(f"   Items with business keywords: {self.stats.get('items_with_business_keywords', 0)}")
        spider.logger.info(f"   Most common domains: {self._get_top_domains(3)}")
        spider.logger.info(f"   Content types: {self._get_content_type_stats()}")

    def _get_top_domains(self, limit=3):
        """Obtiene los dominios más comunes."""
        domain_stats = {k: v for k, v in self.stats.items() if k.startswith('domain_')}
        sorted_domains = sorted(domain_stats.items(), key=lambda x: x[1], reverse=True)
        return [domain.replace('domain_', '') for domain, count in sorted_domains[:limit]]

    def _get_content_type_stats(self):
        """Obtiene estadísticas de tipos de contenido."""
        content_stats = {k: v for k, v in self.stats.items() if k.startswith('content_type_')}
        return {k.replace('content_type_', ''): v for k, v in content_stats.items()}