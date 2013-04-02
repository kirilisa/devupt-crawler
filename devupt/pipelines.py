# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy import signals
from devupt import utils
import json
import re

# cleans whitespace & HTML
class CleanerPipeline(object):
    def process_item(self, item, spider):
        # general tidying up
        for (name, val) in item.items():
            #utils.devlog("Working on %s [%s]" % (name, val))
            if val is None:
                item[name] = ""
                continue
            item[name] = re.sub('\s+', ' ', val).strip() # remove whitespace            
            #item['desc'] = re.sub('<[^<]+?>', '', item['desc']).strip() # remove HTML tags

        # spider specific
        if spider.name == "techmeme":
            item['desc'] = item['desc'].replace('&nbsp; &mdash;&nbsp;', '') 

        return item


# are there duplicate links?
class DuplicateLinksPipeline(object):
    def __init__(self):
        self.pages_seen = set()

    def process_item(self, item, spider):
        if item['link']:
            if item['link'] in self.pages_seen:
                raise DropItem("Duplicate link found: %s" % item)
            else:
                self.pages_seen.add(item['link'])
        return item


# write JSON to file: do not use 
class JsonWriterPipeline(object):
    def open_spider(self, spider):
        if spider.name == 'techmeme':
            self.file = open('json/techmeme.json', 'wb')
        elif spider.name == 'github':
            self.file = open('json/github.json', 'wb')
        elif spider.name == 'coursera':
            self.file = open('json/coursera.json', 'wb')
        elif spider.name == 'meetup':
            self.file = open('json/meetup.json', 'wb')
        return
    
    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

# write to postgres DB
class DBWriterPipeline(object):
    table = ''

    def open_spider(self, spider):
        if spider.name == 'techmeme':
            self.table = 'du_agg_news'
        elif spider.name == 'github':
            self.table = 'du_agg_projects'
        elif spider.name == 'coursera':
            self.table = 'du_agg_courses'
        elif spider.name == 'meetup':
            self.table = 'du_agg_events'
        return
    
    def process_item(self, item, spider):
        return item
