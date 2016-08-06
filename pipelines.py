# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from like123.db_manager import *

class Like123Pipeline(object):
		def process_item(self, item, spider):
				return item

		def close_spider(self, spider):
				CSVFile()
				pass
