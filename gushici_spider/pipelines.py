# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs

class GushiciSpiderPipeline(object):

    def __init__(self):
        self.index = 0
        self.buf = []
        self.output_file = codecs.open('out'+str(self.index)+'.json', 'w',
                                       encoding='utf-8')

    def process_item(self, item, spider):
        self.buf.append(dict(item))
        if len(self.buf) == 5000:
            json.dump(self.buf, self.output_file,
                      sort_keys=True, indent=4,
                      ensure_ascii=False)
            self.output_file.close()
            self.index += 1
            self.output_file = codecs.open('out'+str(self.index)+'.json', 'w',
                                           encoding='utf-8')
            self.buf = []

        return item

    def close_spider(self, spider):
        if len(self.buf) > 0:
            json.dump(self.buf, self.output_file,
                      sort_keys=True, indent=4,
                      ensure_ascii=False)
        self.output_file.close()
