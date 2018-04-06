# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs

class GushiciSpiderPipeline(object):

    def __init__(self):
        self.output_file = codecs.open('out.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.output_file.write(line)
        return item

    def close_spider(self, spider):
        self.output_file.close()
