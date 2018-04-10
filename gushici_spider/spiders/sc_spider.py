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

class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    CYAN = '\033[0;36m'
    RED = '\033[0;31m'
    PURPLE = '\033[0;35m'
    BROWN = '\033[0;33m'
    YELLOW = '\033[1;33m'
    ENDC = '\033[0m'

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
             'Lu': u'\u5f8b\u8bd7',
             'PaiLu': u'\u6392\u5f8b',
             'GuFeng': u'\u53e4\u98ce',
             'Ci': u'\u8bcd',
             'SiYan': u'\u56db\u8a00\u8bd7',
             'LiuYan': u'\u516d\u8a00\u8bd7',
             'Ju': u'\u53e5',
             'QuCi': u'\u4e50\u5e9c\u66f2\u8f9e',
             'Jie': u'\u5048\u9882',
             'Qu': u'\u66f2',
             'ChuCi': u'\u9a9a',}

class GscSpider(CrawlSpider):

    name = "sc_spider"
    start_urls = ["https://sou-yun.com/PoemIndex.aspx"]
    allowed_dpmians = ["sou-yun.com"]
    rules = (
        Rule(LinkExtractor(allow=('/*type=*')),
             follow=False,
             callback='parse_item'),
        Rule(LinkExtractor(allow=('/PoemIndex.aspx\?dynasty=\w+&author=*')),
             follow=False,
             callback='parse_author'),
        Rule(LinkExtractor(allow=('/PoemIndex.aspx\?dynasty=\w+')),
             follow=False,
             callback='parse_dynasty'),
        #Rule(LinkExtractor(allow=('/PoemIndex.aspx'), deny=('/*path*')),
        #     callback='parse_index'),
    )

    #def parse_start_url(self, response):
    #    print Colors.GREEN + response.url + Colors.ENDC
    #    dynasties = response.xpath('//a[contains(@class, "list")]/@href').extract()
    #    print len(dynasties)
    #    for dynasty in dynasties:
    #        yield scrapy.Request(response.urljoin(dynasty))

    def parse_dynasty(self, response):
        print Colors.YELLOW + response.url + Colors.ENDC
        #authors = response.xpath('//div[contains(@class, "list1")]')
        authors_url = response.xpath('//a[contains(@href, "author")]/@href').extract()
        print len(authors_url)
        for author_url in authors_url:
            yield scrapy.Request(response.urljoin(author_url))

    def parse_author(self, response):
        print Colors.RED + response.url + Colors.ENDC
        types = response.xpath('//a[contains(@class, "list")]/@href').extract()
        for typ in types:
            yield scrapy.Request(response.urljoin(typ))

    def parse_item(self, response):
        """
        parse poem
        """
        print Colors.BLUE + response.url + Colors.ENDC
        poem_type = re.search('.*type=(\w+).*', response.url).group(1)
        poem_era = re.search('.*dynasty=(\w+)&author.*', response.url).group(1)
        poem_author = urllib.unquote(re.search('.*author(.*)&type=.*', response.url).group(1))

        items = response.xpath('//div[contains(@id, "item")]')
        for it in items:
            titles = it.xpath('div[contains(@class, "title")]')
            contents = it.xpath('div[contains(@class, "content")]')
            main_title = titles[0].xpath('text()').extract()[0].split(LEFT_BRA)[0]
            sub_n = len(titles)

            for i in range(sub_n):

                item = GushiciSpiderItem()
                item['author'] = poem_author
                item['era'] = ERA_DICT[poem_era]
                item['type'] = poem_type

                title = titles[i].xpath('text()').extract()
                item['title'] = re.search('('+NONASC+'+)'+LEFT_BRA, title[0]).group(1).strip()
                if sub_n > 1:
                    if i == 0:
                        item['title'] = main_title + CH_BLANK + u'\u5176\u4e00'
                    else:
                        item['title'] = main_title + CH_BLANK + item['title']

                item['subtype'] = None
                item['yun'] = None
                if len(title) > 1:
                    yun = re.search(YA_YUN, title[1])
                    item['yun'] = yun.group(1) if yun is not None else None
                    if poem_type == 'Ci':
                        item['subtype'] = item['title'].split(CH_BLANK)[0]
                    else:
                        jiyan = re.search(CH_BLANK+'(\W'+YAN+'\W{2})'+CH_BLANK, title[1])
                        item['subtype'] = jiyan.group(1) if jiyan is not None else None

                item['text'] = []
                for line in contents[i].xpath('p'):
                    str_sentences = line.extract().split('!')
                    for sentence in str_sentences:
                        item['text'].append(''.join(re.findall('>('+NONASC+'+)<', sentence)))

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
