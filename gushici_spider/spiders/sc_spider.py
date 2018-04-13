import scrapy
import re
import urllib
from gushici_spider.items import GushiciSpiderItem

LEFT_BRA = u'\uff08'
RIGHT_BRA = u'\uff09'
NONASC = u'[^\x00-\x7F]'
YA_YUN = u'\u62bc' + '(' + NONASC + ')' + u'\u97f5'
CH_BLANK = u'\u3000'
YAN = u'\u8a00'
C_NUM = u'[\u2460-\u246e]'
QI_YI = u'\u5176\u4e00'

class Colors:
    BLUE = '\033[0;34m'
    GREEN = '\033[0;32m'
    CYAN = '\033[0;36m'
    RED = '\033[0;31m'
    PURPLE = '\033[0;35m'
    BROWN = '\033[0;33m'
    YELLOW = '\033[1;33m'
    ENDC = '\033[0m'

ERA_DICT = {'XianQin': u'\u5148\u79e6', 'Qin': u'\u79e6', 'Han': u'\u6c49',
            'WeiJin': u'\u9b4f\u664b', 'NanBei': u'\u5357\u5317\u671d', 'Sui': u'\u968b',
            'Tang': u'\u5510', 'Song': u'\u5b8b', 'Liao': u'\u8fbd',
            'Jin': u'\u91d1', 'Yuan': u'\u5143', 'Ming': u'\u660e',
            'Qing': u'\u6e05', 'Jindai': u'\u8fd1\u73b0\u4ee3', 'Dangdai': u'\u5f53\u4ee3',}

ERA_D = ''
for era in ERA_DICT.values():
    ERA_D += '|' + LEFT_BRA + era
ERA_D = ERA_D[1:]

TYPE_DICT = {'JieJu': u'\u7edd\u53e5', 'Lu': u'\u5f8b\u8bd7', 'PaiLu': u'\u6392\u5f8b',
             'GuFeng': u'\u53e4\u98ce', 'Ci': u'\u8bcd', 'SiYan': u'\u56db\u8a00\u8bd7',
             'LiuYan': u'\u516d\u8a00\u8bd7', 'Ju': u'\u53e5', 'QuCi': u'\u4e50\u5e9c\u66f2\u8f9e',
             'Jie': u'\u5048\u9882', 'Qu': u'\u66f2', 'Fu': u'\u8f9e\u8d4b',
             'ChuCi': u'\u9a9a',}

class GscSpider(scrapy.Spider):

    name = "sc_spider"
    start_urls = ["https://sou-yun.com/PoemIndex.aspx"]
    allowed_dpmians = ["sou-yun.com"]

    def parse(self, response):
        url = response.url

        if url == "https://sou-yun.com/PoemIndex.aspx":
            for dynasty in self.parse_index(response):
                yield scrapy.Request(response.urljoin(dynasty))
        elif re.match('.*dynasty.*author.*', url) is not None:
            for typ in self.parse_author(response):
                yield scrapy.Request(response.urljoin(typ),
                                     callback=self.parse_item)
        elif re.match('.*dynasty=.*', url) is not None:
            for author in self.parse_dynasty(response):
                yield scrapy.Request(response.urljoin(author))
        else:
            print(Colors.CYAN + 'not match' + Colors.ENDC)

    def parse_index(self, response):
        """
        parse index to dynasties
        """
        print(Colors.GREEN + 'index' + Colors.ENDC)
        print(Colors.GREEN + response.url + Colors.ENDC)
        dynasties = response.xpath('//a[contains(@class, "list")]/@href').extract()
        print(len(dynasties))
        return dynasties

    def parse_dynasty(self, response):
        """
        parse dynasty to authors
        """
        print(Colors.YELLOW + response.url + Colors.ENDC)
        authors = response.xpath('//a[contains(@href, "author")]/@href').extract()
        print(len(authors))
        return authors

    def parse_author(self, response):
        print(Colors.RED + response.url + Colors.ENDC)
        poem_author = urllib.unquote(re.search('.*author=(.*)', response.url).group(1))
        print(Colors.RED + poem_author + Colors.ENDC)
        types = response.xpath('//a[contains(@class, "list")]/@href').extract()
        return types

    def parse_title(self, item):
        titles = item.xpath('div[@class="title"]')
        titles = titles.xpath('string(.)').extract()
        yuns = []
        subtypes = []
        for i in range(len(titles)):
            yun = re.search(YA_YUN, titles[i])
            yuns.append(yun.group(1) if yun is not None else None)
            jiyan = re.search(CH_BLANK+'(\W'+YAN+'\W{2})'+CH_BLANK, titles[i])
            subtypes.append(jiyan.group(1) if jiyan is not None else None)
            titles[i] = re.split(ERA_D, titles[i])[0].strip()
        if len(titles) == 1:
            return titles, yuns, subtypes
        tsplit = []
        for title in titles:
            tsplit.append(re.split(' |'+CH_BLANK, title))
        pos_qi_t0 = len(tsplit[0])
        for i in range(len(tsplit[0])):
            if tsplit[0][i][0] == QI_YI[0] and len(tsplit[0][i]) < 4:
                pos_qi_t0 = i
                break
        pos_qi_t1 = 0
        for i in range(len(tsplit[1])):
            if tsplit[1][i][0] == QI_YI[0] and len(tsplit[1][i]) < 4:
                pos_qi_t1 = i
                break
        main_title = ' '
        if pos_qi_t0 < len(tsplit[0]):
            main_title = ' '.join(tsplit[0][0: pos_qi_t0-pos_qi_t1])
        else:
            main_title = ' '.join(tsplit[0][0: pos_qi_t0-(len(tsplit[1])-1)])
        for i in range(len(tsplit)):
            if i == 0:
                if pos_qi_t0 < len(tsplit[0]):
                    titles[i] = ' '.join(tsplit[0])
                else:
                    tsplit[0].insert(len(tsplit[0])-(len(tsplit[1])-1-pos_qi_t1), QI_YI)
                    titles[i] = ' '.join(tsplit[0])
            else:
                titles[i] = main_title + ' ' + ' '.join(tsplit[i])
        return titles, yuns, subtypes

    def parse_item(self, response):
        """
        parse poem
        """
        print(Colors.BLUE + response.url + Colors.ENDC)
        poem_type = re.search('.*type=(\w+).*', response.url).group(1)
        poem_era = re.search('.*dynasty=(\w+)&author.*', response.url).group(1)
        poem_author = urllib.unquote(re.search('author=(.*)&type', response.url).group(1))
        poem_author = unicode(poem_author, 'utf-8')
        poem_author = ''.join(re.findall(NONASC, poem_author))

        items = response.xpath('//div[contains(@id, "item")]')
        for it in items:
            titles, yuns, subtypes = self.parse_title(it)
            #for t_str in new_titles:
            #    print(t_str)
            #print('****press any key to continue\n')
            #raw_input()
            #titles = it.xpath('div[@class="title"]')
            contents = it.xpath('div[contains(@class, "content")]')
            #main_title = titles[0].xpath('text()').extract()[0].split(LEFT_BRA+ERA_DICT[poem_era])[0].strip()
            sub_n = len(titles)

            for i in range(sub_n):

                item = GushiciSpiderItem()
                item['author'] = poem_author
                item['era'] = ERA_DICT[poem_era]
                item['type'] = TYPE_DICT[poem_type]

                #title = titles[i].xpath('string(.)').extract()[0]
                #item['title'] = title.split(LEFT_BRA+item['era'])[0].strip()
                item['title'] = titles[i]
                #if sub_n > 1:
                #    if i == 0:
                #        item['title'] = main_title + CH_BLANK + u'\u5176\u4e00'
                #    else:
                #        item['title'] = main_title + CH_BLANK + item['title']
                print(Colors.BROWN+item['title']+' '+item['era']+' '+item['author']+Colors.ENDC)

                #yun = re.search(YA_YUN, title)
                #item['yun'] = yun.group(1) if yun is not None else None
                #item['subtype'] = None
                item['yun'] = yuns[i]
                item['subtype'] = subtypes[i]
                #if poem_type == 'Ci':
                #    item['subtype'] = re.split(CH_BLANK+'| |'+LEFT_BRA, item['title'])[0]
                #else:
                #    jiyan = re.search(CH_BLANK+'(\W'+YAN+'\W{2})'+CH_BLANK, title)
                #    item['subtype'] = jiyan.group(1) if jiyan is not None else None

                item['text'] = []
                content_str = re.split('p\>|!', contents[i].extract())
                for line in content_str:
                    sentence = ''.join(re.findall(NONASC, line))
                    sentence = re.sub(LEFT_BRA+'.*'+RIGHT_BRA+'|'+C_NUM+'|'+CH_BLANK, '', sentence)
                    if len(sentence) > 0:
                        item['text'].append(sentence)

                yield item

        #generate next page
        curr_str = re.search('.*=(\d+)', response.url)
        curr = int(curr_str.group(1)) if curr_str is not None else 0
        nex = response.xpath('//div[contains(@class, "poem")]/a/@href').extract()
        if len(nex) == 0:
            return
        next_n = int(re.search('.*=(\d+)', nex[-1]).group(1))
        if next_n == curr + 1:
            yield scrapy.Request(response.urljoin(nex[-1]), callback=self.parse_item)
