import scrapy
import re
import urllib
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from gushici_spider.items import GushiciSpiderItem

LEFT_BRA = u'\uff08'
NONASC = u'[^\x00-\x7F]'
YA_YUN = u'\u62bc' + '(' + NONASC + ')' + u'\u97f5'
CH_BLANK = u'\u3000'
YAN = u'\u8a00'

ERA_DICT = {'XianQin': u'\u5148\u79e6',
            'Qin': u'\u79e6',
            'Han': u'\u6c49',
            'WeiJin': u'\u9b4f\u664b',
            'NanBei': u'\u5357\u5317\u671d',
            'Sui': u'\u968b',
            'Tang': u'\u5510',
            'Song': u'\u5b8b',
            'Liao': u'\u8fbd',
            'Jin': u'\u91d1',
            'Yuan': u'\u5143',
            'Ming': u'\u660e',
            'Qing': u'\u6e05',
            'Jindai': u'\u8fd1\u73b0\u4ee3',
            'Dangdai': u'\u5f53\u4ee3',}

TYPE_DICT = {'JieJu': u'\u7edd\u53e5',
             'Lu': u'\u5f8b\u8bd7',}

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
        poem_type = re.search('.*type=(\w+).*', response.url).group(1)
        poem_era = re.search('.*dynasty=(\w+)&author.*', response.url).group(1)
        poem_author = urllib.unquote(re.search('.*author(.*)&type=.*', response.url).group(1))

        items = response.xpath('//div[contains(@id, "item")]')
        for it in items:
            titles = it.xpath('div[contains(@class, "title")]')
            contents = it.xpath('div[contains(@class, "content")]')

            for i in range(len(titles)):
                item = GushiciSpiderItem()
                item['author'] = poem_author
                item['era'] = ERA_DICT[poem_era]
                item['type'] = poem_type
                title = titles[i].xpath('text()').extract()
                item['title'] = re.search('('+NONASC+'+)'+LEFT_BRA, title[0]).group(1)
                item['subtype'] = None
                item['yun'] = None
                if len(title) > 1:
                    yun = re.search(YA_YUN, title[1])
                    item['yun'] = yun.group(1) if yun is not None else None
                    if poem_type == 'Ci':
                        item['subtype'] = title[0].split(CH_BLANK)[0]
                    else:
                        jiyan = re.search(CH_BLANK+'(\W'+YAN+'\W{2})'+CH_BLANK, title[1])
                        item['subtype'] = jiyan.group(1) if jiyan is not None else None


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
