import scrapy
import re
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
        item['url'] = re.search('.*shiwenv_(\w+).aspx', response.url).group(1)
        item['title'] = response.xpath('//h1[contains(@style, "font-size:20px")]/text()').extract()[0]
        item['author'] = response.xpath('//p/a[contains(@href, "authorv")]/text()').extract()[0]
        item['era'] = response.xpath('//p/a[contains(@href, "shiwen")]/text()').extract()[0]

        cont_resp = response.xpath('//div[contains(@id, "contson")]')[0]
        pre_text = cont_resp.xpath('p/span/text()').extract()
        item['pre_text'] = []
        for sentance in pre_text:
            item['pre_text'].append(sentance)
        text = None
        if len(pre_text) > 0:
            text = cont_resp.xpath('p/text()').extract()
        else:
            text = cont_resp.xpath('text()').extract()
        item['text'] = []
        for sentance in text:
            item['text'].append(sentance)
        return item
