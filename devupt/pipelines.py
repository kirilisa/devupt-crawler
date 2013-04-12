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
from random import randrange

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

# write to postgres DB
class DBWriterPipeline(object):    
    table = ''
    cols = []
    keysvals = {}
    conn = None 
    cur = None
    bad = 0

    def open_spider(self, spider):        
        # decide tables and columns to populate
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

        # open database for writing
        try:
            self.conn = psycopg2.connect(database='devupt_db', user='duagg', password='crunch1ngs') 
            self.cur = self.conn.cursor()
            
        except psycopg2.DatabaseError, e:
            print "Could not connect to database: %s" % e    
        
    def process_item(self, item, spider):                
        try:
            # attempt to get get spider source
            self.cur.execute("select id from du_agg_sources where slug=%s;", (spider.name,)) 
            #print "QRY: %s, CNT: %s" % (self.cur.query, self.cur.rowcount)
            if not self.cur.rowcount:
                return item
            else:
                item['src'] = self.cur.fetchone()[0]         

            #@@@ attempt to get language ref if necessary
            if (spider.name == 'github') :
                item['stars'] = 0 if not item['stars'] else item['stars']
                item['forks'] = 0 if not item['stars'] else item['forks']
                self.cur.execute("select id from du_agg_languages where slug = %s or lower(title) = %s;", (item['lang'].lower(), item['lang'].lower())) 
                #print "QRY: %s, CNT: %s" % (self.cur.query, self.cur.rowcount)
                if not self.cur.rowcount:
                    self.bad += 1
                    return item
                else:                    
                    item['lang'] = self.cur.fetchone()[0]
                    print "\nLANGUAGE IS NOW: %s" % item['lang']

            # populate dict with fields/vals
            keysvals = dict.fromkeys(self.cols)
            for col in keysvals:
                keysvals[col] = item[col]

            # generate SQL and insert into the DB
            datarep = ("%s," * len(keysvals)).rstrip(',')
            sql = "insert into %s (%s) values (%s);" % (self.table, ', '.join(keysvals.keys()), datarep)            
            print "\nSQL: %s ||| %s\n" % (sql, keysvals.values())
            self.cur.execute(sql, keysvals.values())
            print "QRY: %s" % self.cur.query
            self.conn.commit() # maybe should commit in close_spider instead?

        except psycopg2.DatabaseError, e:
            if self.conn:
                self.conn.rollback()
            print "Failed to write DB: %s" % e  

        return item

    def close_spider(self, spider):
        if self.conn:
            self.conn.close()

        print "\nBAD COUNT: %s" % self.bad
