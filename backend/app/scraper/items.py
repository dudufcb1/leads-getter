"""
Items de Scrapy para el sistema de generación de leads.
"""

import scrapy


class LeadItem(scrapy.Item):
    """Item para leads encontrados."""
    url = scrapy.Field()
    domain = scrapy.Field()
    language = scrapy.Field()
    status = scrapy.Field()
    depth_level = scrapy.Field()
    source_url = scrapy.Field()
    emails = scrapy.Field()  # Lista de emails encontrados


class EmailItem(scrapy.Item):
    """Item para emails encontrados."""
    email = scrapy.Field()
    source_page = scrapy.Field()
    website_url = scrapy.Field()