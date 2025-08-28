"""
Pipelines adicionales de filtrado para el sistema de scraping.
"""

import re
from scrapy.exceptions import DropItem
from sqlalchemy.orm import sessionmaker
from ..database.database import engine
from ..database.models import Website

class BusinessRelevancePipeline:
    """Pipeline para filtrar contenido basado en relevancia para negocios."""
    
    def __init__(self):
        """Inicializa el pipeline."""
        self.business_keywords = [
            'empresa', 'compañía', 'servicio', 'producto', 'contacto', 'teléfono',
            'dirección', 'email', 'sitio web', 'negocio', 'cliente', 'venta',
            'comercial', 'oferta', 'promoción', 'descuento', 'cotización',
            'presupuesto', 'facturación', 'proveedor', 'distribuidor'
        ]
        
        # Palabras clave que indican contenido no comercial
        self.non_business_keywords = [
            'blog', 'noticia', 'artículo', 'post', 'news', 'article',
            'personal', 'privado', 'privacidad', 'política', 'terms',
            'condiciones', 'legal', 'copyright', 'about', 'acerca'
        ]
    
    def process_item(self, item, spider):
        """
        Procesa un item y lo filtra basado en relevancia para negocios.
        
        - **item**: Item a procesar
        - **spider**: Spider que generó el item
        """
        # Obtener texto del título, descripción y URL
        title = item.get('title', '') or ''
        description = item.get('description', '') or ''
        url = item.get('url', '') or ''
        
        # Convertir a minúsculas para comparación
        text_content = ' '.join([title, description, url]).lower()
        
        # Contar palabras clave de negocio
        business_score = 0
        for keyword in self.business_keywords:
            if keyword.lower() in text_content:
                business_score += 1
        
        # Contar palabras clave no comerciales
        non_business_score = 0
        for keyword in self.non_business_keywords:
            if keyword.lower() in text_content:
                non_business_score += 1
        
        # Calcular puntuación de relevancia
        relevance_score = business_score - non_business_score
        
        # Si la puntuación es negativa, filtrar el item
        if relevance_score < 0:
            spider.logger.debug(f"🔍 Filtering out non-business content: {url}")
            raise DropItem(f"Non-business content: {url}")
        
        # Agregar puntuación de relevancia al item
        item['business_relevance_score'] = relevance_score
        
        return item

class EmailValidationPipeline:
    """Pipeline para validar emails encontrados."""
    
    def __init__(self):
        """Inicializa el pipeline."""
        # Patrones para emails temporal o de spam
        self.temporary_email_domains = [
            '10minutemail.com', 'guerrillamail.com', 'mailinator.com', 'yopmail.com',
            'throwaway.email', 'getnada.com', 'maildrop.cc', 'temp-mail.org',
            'tempmail.org', 'fake.com', 'test.com', 'spam.com'
        ]
        
        # Patrones para emails de prueba
        self.test_patterns = [
            r'test@', r'admin@', r'root@', r'noreply@', r'do-not-reply@',
            r'system@', r'mailer@', r'daemon@', r'postmaster@', r'abuse@',
            r'webmaster@', r'hostmaster@', r'info@', r'support@'
        ]
    
    def process_item(self, item, spider):
        """
        Procesa un item y valida los emails encontrados.
        
        - **item**: Item a procesar
        - **spider**: Spider que generó el item
        """
        emails = item.get('emails', [])
        if not emails:
            return item
        
        # Validar cada email
        valid_emails = []
        for email in emails:
            if self._is_valid_email(email):
                valid_emails.append(email)
            else:
                spider.logger.debug(f"📧 Filtering out invalid email: {email}")
        
        # Si no quedan emails válidos, filtrar el item
        if not valid_emails:
            url = item.get('url', 'unknown')
            spider.logger.debug(f"📧 No valid emails found, filtering item: {url}")
            raise DropItem(f"No valid emails: {url}")
        
        # Actualizar lista de emails con los válidos
        item['emails'] = valid_emails
        item['valid_email_count'] = len(valid_emails)
        
        return item
    
    def _is_valid_email(self, email):
        """
        Verifica si un email es válido.
        
        - **email**: Email a validar
        """
        if not email:
            return False
        
        # Verificar formato básico
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False
        
        # Verificar dominio temporal
        domain = email.split('@')[1]
        if domain in self.temporary_email_domains:
            return False
        
        # Verificar patrones de prueba
        for pattern in self.test_patterns:
            if re.search(pattern, email, re.IGNORECASE):
                return False
        
        return True

class ContentQualityPipeline:
    """Pipeline para evaluar la calidad del contenido."""
    
    def __init__(self):
        """Inicializa el pipeline."""
        # Palabras clave que indican contenido de baja calidad
        self.low_quality_keywords = [
            'click here', 'buy now', 'limited time', 'act now', 'free offer',
            'guarantee', 'no risk', 'cash back', 'money back', 'risk free',
            'miracle', 'cure', 'lose weight', 'get rich', 'make money'
        ]
        
        # Palabras clave que indican contenido de alta calidad
        self.high_quality_keywords = [
            'research', 'study', 'analysis', 'report', 'documentation',
            'guide', 'tutorial', 'manual', 'specification', 'whitepaper',
            'case study', 'best practices', 'expert', 'professional'
        ]
    
    def process_item(self, item, spider):
        """
        Procesa un item y evalúa la calidad del contenido.
        
        - **item**: Item a procesar
        - **spider**: Spider que generó el item
        """
        # Obtener texto del título, descripción y URL
        title = item.get('title', '') or ''
        description = item.get('description', '') or ''
        url = item.get('url', '') or ''
        
        # Convertir a minúsculas para comparación
        text_content = ' '.join([title, description, url]).lower()
        
        # Contar palabras clave de baja calidad
        low_quality_score = 0
        for keyword in self.low_quality_keywords:
            if keyword.lower() in text_content:
                low_quality_score += 1
        
        # Contar palabras clave de alta calidad
        high_quality_score = 0
        for keyword in self.high_quality_keywords:
            if keyword.lower() in text_content:
                high_quality_score += 1
        
        # Calcular puntuación de calidad
        quality_score = high_quality_score - low_quality_score
        
        # Si la puntuación es muy negativa, filtrar el item
        if quality_score < -2:
            url = item.get('url', 'unknown')
            spider.logger.debug(f"📊 Filtering out low quality content: {url}")
            raise DropItem(f"Low quality content: {url}")
        
        # Agregar puntuación de calidad al item
        item['content_quality_score'] = quality_score
        
        return item

class DuplicateContentPipeline:
    """Pipeline para detectar y filtrar contenido duplicado."""
    
    def __init__(self):
        """Inicializa el pipeline."""
        # Conexión a la base de datos
        self.Session = sessionmaker(bind=engine)
        self.seen_content_hashes = set()
    
    def process_item(self, item, spider):
        """
        Procesa un item y lo filtra si es duplicado.
        
        - **item**: Item a procesar
        - **spider**: Spider que generó el item
        """
        # Generar hash del contenido
        content_hash = self._generate_content_hash(item)
        
        # Verificar si ya hemos visto este contenido
        if content_hash in self.seen_content_hashes:
            url = item.get('url', 'unknown')
            spider.logger.debug(f"📄 Filtering out duplicate content: {url}")
            raise DropItem(f"Duplicate content: {url}")
        
        # Verificar en la base de datos
        if self._is_duplicate_in_database(content_hash):
            url = item.get('url', 'unknown')
            spider.logger.debug(f"📄 Filtering out duplicate content (DB): {url}")
            raise DropItem(f"Duplicate content (DB): {url}")
        
        # Registrar como visto
        self.seen_content_hashes.add(content_hash)
        
        # Agregar hash al item
        item['content_hash'] = content_hash
        
        return item
    
    def _generate_content_hash(self, item):
        """
        Genera un hash del contenido del item.
        
        - **item**: Item del cual generar el hash
        """
        # Combinar título, descripción y dominio
        title = item.get('title', '') or ''
        description = item.get('description', '') or ''
        domain = item.get('domain', '') or ''
        
        content = f"{title}|{description}|{domain}"
        return hash(content)
    
    def _is_duplicate_in_database(self, content_hash):
        """
        Verifica si el contenido ya existe en la base de datos.
        
        - **content_hash**: Hash del contenido a verificar
        """
        try:
            session = self.Session()
            # Buscar sitios web con el mismo hash de contenido
            existing_website = session.query(Website).filter_by(
                fingerprint=str(content_hash)
            ).first()
            session.close()
            
            return existing_website is not None
        except Exception:
            # En caso de error, asumir que no es duplicado
            return False

# Exportar los pipelines
__all__ = [
    'BusinessRelevancePipeline',
    'EmailValidationPipeline',
    'ContentQualityPipeline',
    'DuplicateContentPipeline'
]