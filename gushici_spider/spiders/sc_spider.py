import scrapy
import re
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from gushici_spider.items import GushiciSpiderItem

class GscSpider(CrawlSpider):

    name = "sc_spider"
    start_urls = ["https://sou-yun.com/PoemIndex.aspx?"]
    allowed_dpmians = ["sou-yun.com"]
    rules = (
        Rule(LinkExtractor(allow=('/P*dynasty=*author=*type=*')),
             callback='parse_item'),
        Rule(LinkExtractor(allow=('/P*dynasty=*author=*')),
             callback='parse_author'),
        Rule(LinkExtractor(allow=('/P*dynasty=*')),
             callback='parse_dynasty'),
    )

    def parse_dynasty(self, response):

        authors = response.xpath('//div[contains(@class, "list1")]')
        authors_url = authors.xpath('div[contains(@class, "inline")]/a/@href').extract()
        for author_url in authors_url:
            yield scrapy.Request(response.urljoin(author_url))

    def parse_author(self, response):
        types = response.xpath('//a[contains(@class, "list")]/@href').extract()
        for typ in types:
            yield scrapy.Request(response.urljoin(typ))

    def parse_item(self, response):
        """
        parse poem
        """
        items = response.xpath('//div[contains(@id, "item")]')
        for it in items:
            item = GushiciSpiderItem()
            item['title'] = []
            for title in it.xpath('div[contains(@class, "title")]/text()').extract():
                item['title'].append(title)
            item['url'] = re.search('.*shiwenv_(\w+).aspx', response.url).group(1)
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
        yield item

        #generate next page
        curr_str = re.search('.*=(\d+)', response.url)
        curr = int(curr_str.group(1)) if curr_str is not None else 0
        nex = response.xpath('//div[contains(@class, "poem")]/a/@href').extract()
        if nex is None:
            return
        next_n = int(re.search('.*=(\d+)', nex[-1]).group(1))
        if next_n == curr + 1:
            yield scrapy.Request(response.urljoin(nex[-1]))
