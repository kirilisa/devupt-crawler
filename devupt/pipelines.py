# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.exceptions import DropItem
from scrapy import signals
from devupt import utils
import json
import re
import psycopg2
import sys
import urlparse
import os
from random import randrange
from scrapy import log

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
            #item['blurb'] = re.sub('<[^<]+?>', '', item['blurb']).strip() # remove HTML tags

        # spider specific
        if spider.name == "techmeme":
            item['blurb'] = item['blurb'].replace('&nbsp; &mdash;&nbsp;', '').strip()

        return item


# are there duplicate links?
class DuplicateLinksPipeline(object):
    def __init__(self):
        self.pages_seen = set()

    def process_item(self, item, spider):
        if item['link']:
            if item['link'] in self.pages_seen:
                utils.devlog("Link '%s' is a duplicate!" % item['link'], 'w')
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
        line = line.replace("{", "[")
        line = line.replace("}", "]")
        self.file.write(line)
        return item

    def close_spider(self, spider):
        self.file.close()

# write data to postgres DB
class DBWriterPipeline(object):    
    table = ''
    cols = []
    conn = None 
    cur = None
    bad = 0

    # sets the crawler gotten from the classmethod below
    def __init__(self, crawler):
        self.crawler = crawler

    # need this so we have access to the crawler engine
    # and can manually shut the spider down if need be
    @classmethod 
    def from_crawler(cls, crawler):
        ext = cls(crawler)
        return ext
        
    def open_spider(self, spider):
        # designate table and fields to populate
        if spider.name in ['techmeme']:
            self.table = 'du_agg_news'
            self.cols = ['title', 'link', 'blurb', 'src']
        elif spider.name in ['github']:
            self.table = 'du_agg_projects'
            self.cols = ['title', 'link', 'blurb', 'lang', 'updated', 'stars', 'forks', 'src']
        elif spider.name in ['coursera']:
            self.table = 'du_agg_courses'
            self.cols = ['title', 'link', 'blurb', 'school', 'school_link', 'course_date', 'course_length', 'src']
        elif spider.name in ['meetup']:
            self.table = 'du_agg_events'
            self.cols = ['title', 'link', 'blurb', 'host', 'location', 'event_date', 'event_time', 'src']
        else:
            utils.devlog('Cannot get database table for type %s' % spider.name, 'e')
            self.crawler.engine.close_spider(spider, 'Closed spider -- cannot get appropriate database table.')
            
        # connect to database
        try:
            urlparse.uses_netloc.append('postgres') # set parsing scheme
            url = urlparse.urlparse(os.environ['DATABASE_URL'])            
            self.conn = psycopg2.connect("dbname=%s user=%s password=%s host=%s " % (url.path[1:], url.username, url.password, url.hostname))                        
            self.cur = self.conn.cursor()
        except KeyError, e:
            utils.devlog("No DATABASE_URL is set - cannot get database connection information.", 'e')
            self.crawler.engine.close_spider(spider, 'Closed spider -- cannot get database connection information.')
        except psycopg2.DatabaseError, e:
            utils.devlog("Could not connect to database: %s" % e, 'e')
            self.crawler.engine.close_spider(spider, 'Closed spider -- cannot connect to database.')
        
    def process_item(self, item, spider):                
        try:
            # attempt to get get spider source
            self.cur.execute("select id from du_agg_sources where slug=%s;", (spider.name,)) 
            if not self.cur.rowcount:
                return item
            else:
                item['src'] = self.cur.fetchone()[0]         

            #@@@ attempt to get language ref if necessary
            if (spider.name == 'github') :
                item['stars'] = 0 if not item['stars'] else item['stars']
                item['forks'] = 0 if not item['stars'] else item['forks']
                self.cur.execute("select id from du_agg_languages where slug = %s or lower(title) = %s;", (item['lang'].lower(), item['lang'].lower())) 
                if not self.cur.rowcount:
                    self.bad += 1
                    return item
                else:                    
                    item['lang'] = self.cur.fetchone()[0]

            # populate dict with fields/vals
            keysvals = dict.fromkeys(self.cols)
            for col in keysvals:
                keysvals[col] = item[col]

            # generate SQL and insert into the DB
            datarep = ("%s," * len(keysvals)).rstrip(',')
            sql = "insert into %s (%s) values (%s);" % (self.table, ', '.join(keysvals.keys()), datarep)            
            self.cur.execute(sql, keysvals.values())
            #utils.devlog("QRY: %s" % self.cur.query)
            self.conn.commit() # maybe should commit in close_spider instead of for each item

        except psycopg2.DatabaseError, e:
            if self.conn:
                self.conn.rollback()
            self.bad += 1
            utils.devlog("Failed to store itemed entitled '%s' via %s spider: %s" % (item['title'], spider.name, e))

        return item

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()
        utils.devlog("Number of items not stored: %s" % self.bad)
