from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from devupt import utils
from devupt.items import CourseItem
import urlparse
import json
import re

class CourseraSpider(BaseSpider):
    name = "coursera"
    allowed_domains = ["coursera.com"]
    start_urls = [
        #"https://www.coursera.org/courses?orderby=upcoming&cats=cs-programming"
        "https://www.coursera.org/maestro/api/topic/list"
        ]
    cats = ["cs-programming"] # pretty crappy
    item_cnt = 0

    def parse(self, response):
        courses = json.loads(response.body) # grab the JSON from the API search
        for course in courses:
            if self.cats[0] in course['category-ids']:
                item = CourseItem()
                item['title'] = course['name']
                item['blurb'] = course['short_description']
                item['link'] = urlparse.urljoin("https://www.coursera.org/course/", course['short_name'])
                item['school'] = course['universities'][0]['name']
                item['school_link'] = urlparse.urljoin("http://coursera.org/", course['universities'][0]['short_name'])
                item['course_date'] = "TBA" if course['courses'][0]['start_date_string'] in [None, ""] else course['courses'][0]['start_date_string']
                item['course_length'] = "TBA" if course['courses'][0]['duration_string'] in [None, ""] else course['courses'][0]['duration_string']
                item['src'] = "courses"

                self.item_cnt += 1
                yield item

        utils.devlog("All done... total items is %d" % self.item_cnt)

        
