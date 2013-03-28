# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy import signals
import json
import re

class DevuptPipeline(object):
    def process_item(self, item, spider):
        return item

class CleanerPipeline(object):
    def process_item(self, item, spider):
        # general whitespace removal
        for (name, val) in item.items():
            #print "Working on " + name + " which has value " + val + "\n"
            item[name] = re.sub('\s+', ' ', val).strip() # remove whitespace
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

# do not use 
class JsonWriterPipeline(object):
    def __init__(self):
        self.file = open('items.jl', 'wb')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item
