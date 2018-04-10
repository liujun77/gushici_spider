# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class GushiciSpiderItem(scrapy.Item):
    """
    gushici item
    """
    # define the fields for your item here like:
    title = scrapy.Field()
    author = scrapy.Field()
    era = scrapy.Field()
    text = scrapy.Field()
    type = scrapy.Field()
    subtype = scrapy.Field()
    yun = scrapy.Field()
