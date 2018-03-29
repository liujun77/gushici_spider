import scrapy

class SC_Spider_Xpath(scrapy.Spider):

    name = "sc_spider_xpath"
    start_urls = ["https://www.gushiwen.org/"]
    allowed_dpmians = ["gushiwen.org"]

    def parse(self, response):

        for next_url in response.xpath("//a/@href").extract():
            if next_url is not None:
                yield scrapy.Request(response.urljoin(next_url))
