"""
Spider principal para scraping de leads.
"""

import re
import scrapy
from urllib.parse import urlparse, urljoin
from ..items import LeadItem, EmailItem


class LeadSpider(scrapy.Spider):
    """Spider para encontrar leads en páginas web."""

    name = 'lead_spider'
    allowed_domains = []  # Se configura dinámicamente

    def __init__(self, start_url=None, depth=3, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_url = start_url
        self.max_depth = int(depth)  # Asegurar que sea entero
        self.current_depth = 0

        if start_url:
            parsed = urlparse(start_url)
            self.allowed_domains = [parsed.netloc]

    def start_requests(self):
        """Inicia el scraping desde la URL proporcionada."""
        if self.start_url:
            yield scrapy.Request(
                url=self.start_url,
                callback=self.parse,
                meta={'depth': 0, 'source_url': None}
            )

    def parse(self, response):
        """Parsea una página web en busca de leads con manejo robusto de errores."""
        try:
            current_depth = response.meta.get('depth', 0)
            source_url = response.meta.get('source_url')

            # Verificar si la respuesta es válida
            if not self._is_valid_response(response):
                self.logger.warning(f"⚠️ Invalid response for URL: {response.url} - Status: {response.status}")
                return

            # Extraer información de la página actual
            lead_item = self.extract_lead_info(response, current_depth, source_url)

            if lead_item:
                self.logger.info(f"🔄 Yielding lead item for URL: {response.url}")
                self.logger.info(f"📊 Item data: {dict(lead_item)}")
                yield lead_item
            else:
                self.logger.warning(f"⚠️ No lead item created for URL: {response.url}")

            # Si no hemos alcanzado la profundidad máxima, seguir explorando
            if current_depth < self.max_depth:
                yield from self._extract_and_follow_links(response, current_depth)

        except Exception as e:
            self.logger.error(f"❌ Error parsing {response.url}: {str(e)}")
            self._handle_parse_error(response, e)

    def _is_valid_response(self, response):
        """Verifica si la respuesta es válida para procesar."""
        # Verificar código de estado
        if response.status >= 400:
            return False

        # Verificar tipo de contenido
        content_type = response.headers.get('Content-Type', b'').decode('utf-8').lower()
        if 'text/html' not in content_type and 'application/xhtml' not in content_type:
            return False

        # Verificar tamaño mínimo de contenido
        if len(response.body) < 100:  # Menos de 100 bytes probablemente no es una página útil
            return False

        return True

    def _extract_and_follow_links(self, response, current_depth):
        """Extrae y sigue enlaces con manejo de errores."""
        try:
            # Encontrar enlaces en la página
            links = response.css('a::attr(href)').getall()

            for link in links:
                try:
                    # Convertir URLs relativas a absolutas
                    absolute_url = urljoin(response.url, link)

                    # Validar y filtrar URLs
                    if not self._is_valid_url(absolute_url):
                        continue

                    # Verificar que el dominio esté permitido
                    parsed_link = urlparse(absolute_url)
                    if parsed_link.netloc in self.allowed_domains:
                        self.logger.info(f"🔗 Following link: {absolute_url} (depth: {current_depth + 1})")
                        yield scrapy.Request(
                            url=absolute_url,
                            callback=self.parse,
                            meta={
                                'depth': current_depth + 1,
                                'source_url': response.url
                            },
                            errback=self._handle_request_error
                        )

                except Exception as e:
                    self.logger.warning(f"⚠️ Error processing link '{link}': {str(e)}")
                    continue

        except Exception as e:
            self.logger.error(f"❌ Error extracting links from {response.url}: {str(e)}")

    def _is_valid_url(self, url):
        """Valida si una URL es adecuada para scraping."""
        try:
            parsed = urlparse(url)

            # Verificar que tenga esquema válido
            if parsed.scheme not in ['http', 'https']:
                return False

            # Verificar que tenga dominio
            if not parsed.netloc:
                return False

            # Evitar URLs con fragmentos largos (posiblemente spam)
            if len(parsed.fragment) > 200:
                return False

            # Evitar URLs con queries muy largas
            if len(parsed.query) > 500:
                return False

            # Lista negra de patrones comunes de spam
            blacklist_patterns = [
                r'\.(pdf|doc|docx|xls|xlsx|ppt|pptx|zip|rar|exe|dmg|deb|rpm)$',
                r'mailto:',
                r'javascript:',
                r'tel:',
                r'#',
                r'\bwp-admin\b',
                r'\bwp-login\b',
                r'\badmin\b',
                r'\blogin\b'
            ]

            url_lower = url.lower()
            for pattern in blacklist_patterns:
                if re.search(pattern, url_lower):
                    return False

            return True

        except Exception:
            return False

    def _handle_request_error(self, failure):
        """Maneja errores de requests."""
        self.logger.error(f"❌ Request failed: {failure.request.url} - {failure.getErrorMessage()}")

        # Aquí se podría implementar lógica adicional como:
        # - Reintentar con diferentes user-agents
        # - Marcar el dominio como problemático
        # - Notificar a un sistema de monitoreo

    def _handle_parse_error(self, response, error):
        """Maneja errores durante el parsing."""
        self.logger.error(f"❌ Parse error for {response.url}: {str(error)}")

        # Log additional context
        self.logger.debug(f"Response status: {response.status}")
        self.logger.debug(f"Response length: {len(response.body) if hasattr(response, 'body') else 'N/A'}")

    def extract_lead_info(self, response, depth, source_url):
        """Extrae información de lead de una página."""
        # Extraer emails usando múltiples patrones avanzados
        emails = self.extract_emails_advanced(response.text)

        # Para debugging: crear lead item incluso sin emails
        # En producción, se puede volver a activar este filtro
        # if not emails:
        #     return None

        # Extraer dominio
        parsed_url = urlparse(response.url)
        domain = parsed_url.netloc

        # Detectar idioma (básico - se puede mejorar)
        language = self.detect_language(response.text)

        # Crear lead item
        lead_item = LeadItem()
        lead_item['url'] = response.url
        lead_item['domain'] = domain
        lead_item['language'] = language
        lead_item['status'] = 'processed'
        lead_item['depth_level'] = depth
        lead_item['source_url'] = source_url
        lead_item['emails'] = emails

        return lead_item

    def extract_emails_advanced(self, text):
        """Extrae emails usando múltiples patrones avanzados y robustos."""
        emails = set()  # Usar set para evitar duplicados

        # Patrón básico mejorado con caracteres especiales adicionales
        basic_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails.update(re.findall(basic_pattern, text, re.IGNORECASE))

        # Patrón para emails con subdominios múltiples
        subdomain_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails.update(re.findall(subdomain_pattern, text, re.IGNORECASE))

        # Patrón para emails con TLDs largos (.museum, .international, etc.)
        long_tld_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{3,}\b'
        emails.update(re.findall(long_tld_pattern, text, re.IGNORECASE))

        # Patrón para emails en texto con formato especial
        special_patterns = [
            r'mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # mailto: links
            r'email:\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # email: prefix
            r'correo:\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # correo: prefix (español)
            r'e-mail:\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # e-mail: prefix
            r'contact:\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # contact: prefix
            r'contacto:\s*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # contacto: prefix (español)
            r'info@\w+\.\w+',  # info@ pattern
            r'contact@\w+\.\w+',  # contact@ pattern
            r'support@\w+\.\w+',  # support@ pattern
            r'sales@\w+\.\w+',  # sales@ pattern
            r'admin@\w+\.\w+',  # admin@ pattern
            r'hello@\w+\.\w+',  # hello@ pattern
            r'hi@\w+\.\w+',  # hi@ pattern
            r'team@\w+\.\w+',  # team@ pattern
            r'help@\w+\.\w+',  # help@ pattern
            r'service@\w+\.\w+',  # service@ pattern
            r'business@\w+\.\w+',  # business@ pattern
            r'inquiry@\w+\.\w+',  # inquiry@ pattern
            r'feedback@\w+\.\w+',  # feedback@ pattern
        ]

        for pattern in special_patterns:
            emails.update(re.findall(pattern, text, re.IGNORECASE))

        # Patrón para emails ofuscados (comunes en web scraping)
        obfuscated_patterns = [
            r'([A-Za-z0-9._%+-]+)\s*@\s*([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # email con espacios
            r'([A-Za-z0-9._%+-]+)\s*\[at\]\s*([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # [at] format
            r'([A-Za-z0-9._%+-]+)\s*\(at\)\s*([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # (at) format
            r'([A-Za-z0-9._%+-]+)\s*@\s*s\s*([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # @ s @ format
            r'([A-Za-z0-9._%+-]+)\s*@\s*NOSPAM\s*([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # @ NOSPAM @ format
            r'([A-Za-z0-9._%+-]+)\s*@\s*no\s*spam\s*([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # @ no spam @ format
            r'([A-Za-z0-9._%+-]+)\s*@\s*remove\s*me\s*([A-Za-z0-9.-]+\.[A-Z|a-z]{2,})',  # @ remove me @ format
        ]

        for pattern in obfuscated_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for user, domain in matches:
                emails.add(f"{user}@{domain}")

        # Patrón para emails en JavaScript
        js_patterns = [
            r'["\']([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})["\']',  # emails en strings JS
            r'\\u0040',  # @ codificado en unicode
            r'\\x40',  # @ codificado en hex
        ]

        for pattern in js_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if '@' in match:
                    emails.add(match)
                elif match in ['\\u0040', '\\x40']:
                    # Manejar casos donde el @ está codificado
                    # Esto requeriría lógica adicional para reconstruir el email completo
                    pass

        # Patrón para emails en formularios HTML
        html_form_patterns = [
            r'value\s*=\s*["\']([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})["\']',  # value en inputs
            r'placeholder\s*=\s*["\']([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})["\']',  # placeholder
        ]

        for pattern in html_form_patterns:
            emails.update(re.findall(pattern, text, re.IGNORECASE))

        # Patrón para emails en metadatos y comentarios
        metadata_patterns = [
            r'<!--.*?([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}).*?-->',  # emails en comentarios HTML
            r'<meta.*?content\s*=\s*["\']([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})["\']',  # emails en meta tags
        ]

        for pattern in metadata_patterns:
            emails.update(re.findall(pattern, text, re.IGNORECASE | re.DOTALL))

        # Filtrar emails válidos y limpiar
        valid_emails = []
        for email in emails:
            email = email.strip().lower()
            # Validación básica adicional
            if self.is_valid_email_format(email):
                valid_emails.append(email)

        return list(valid_emails)

    def is_valid_email_format(self, email):
        """Valida el formato básico de un email."""
        if not email or len(email) > 254:
            return False

        # Patrón de validación RFC 5322 simplificado
        pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        return bool(re.match(pattern, email, re.IGNORECASE))

    def detect_language(self, text):
        """Detecta el idioma del texto de forma básica."""
        # Implementación básica - se puede mejorar con librerías como langdetect
        spanish_words = ['el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no']
        english_words = ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of']

        text_lower = text.lower()

        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        english_count = sum(1 for word in english_words if word in text_lower)

        if spanish_count > english_count:
            return 'es'
        elif english_count > spanish_count:
            return 'en'
        else:
            return 'unknown'