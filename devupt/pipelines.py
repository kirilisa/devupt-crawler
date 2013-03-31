# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy import signals
from scrapy import log
import json
import re

# cleans whitespace & HTML
class CleanerPipeline(object):
    def process_item(self, item, spider):
        print "Processing item!"
        # general whitespace removal
        item['desc'] = item['desc'].replace('&nbsp; &mdash;&nbsp;', '') # this sucks
        for (name, val) in item.items():
            print "Working on %s [%s]" % (name, val)
            if val is None:
                print "%s was none!!!!!" % name
                item[name] = ""
                continue
            item[name] = re.sub('\s+', ' ', val).strip() # remove whitespace
            #item[name] = re.sub('^&nbsp; &mdash;&nbsp;', '', val).strip();
            #item['desc'] = re.sub('<[^<]+?>', '', item['desc']).strip() # remove HTML tags
        return item


# are there duplicate links?
class DuplicateLinksPipeline(object):
    def __init__(self):
        self.pages_seen = set()

    def process_item(self, item, spider):
        if item['link'] in self.pages_seen:
            raise DropItem("Duplicate link found: %s" % item)
        else:
            self.pages_seen.add(item['link'])
            return item


# write JSON to file: do not use 
class JsonWriterPipeline(object):
    def open_spider(self, spider):
        if spider.name == 'techmeme':
            self.file = open('techmeme.json', 'wb')
        elif spider.name == 'github':
            self.file = open('github.json', 'wb')
        elif spider.name == 'coursera':
            self.file = open('coursera.json', 'wb')
        elif spider.name == 'meetup':
            self.file = open('meetup.json', 'wb')
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
        return
    
    def process_item(self, item, spider):
        return item
