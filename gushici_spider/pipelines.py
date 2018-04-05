# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json


class GushiciSpiderPipeline(object):

    def __init__(self):
        self.output_file = open("output.json", 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.output_file.write(line)
        return item

    def close_spider(self, spider):
        self.output_file.close()
