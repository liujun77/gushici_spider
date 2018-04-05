import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from gushici_spider.items import GushiciSpiderItem

class GscSpider(CrawlSpider):

    name = "sc_spider"
    start_urls = ["https://www.gushiwen.org/"]
    allowed_dpmians = ["gushiwen.org"]
    rules = (
        Rule(LinkExtractor(allow=('/authors/*',),
                           deny=('/guwen/*', '/mingju/*')), follow=True),
        Rule(LinkExtractor(allow=('/shiwenv_*')), callback='parse_item'),
    )

    def parse_item(self, response):
        """
        parse poem
        """
        item = GushiciSpiderItem()
        print response.url + "liujun77"
        return item
