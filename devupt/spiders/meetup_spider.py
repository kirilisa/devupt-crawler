from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy import log
from devupt.items import EventItem
from devupt.colors import bcolors
import urlparse
import re

class MeetupSpider(BaseSpider):
    name = "meetup"
    allowed_domains = ["meetup.com"]
    start_urls = [
        "http://www.meetup.com/find/?categories=34&radius=10&userFreeform=San+Francisco&sort=default" # tech category
        ]
    item_cnt = 0

    def parse(self, response):
        self.log('Parsing page... depth is %s' % response.meta['depth'])
        
        # grab info from events on this page
        hxs = HtmlXPathSelector(response)        
        for event in hxs.select('//div[contains(@class, "simple-card")]'):
            if event.select('.//p[contains(@class, "muted")]/text()').extract(): # only meetups with upcoming meetup
                #@@@ need to crawl further for descriptions etc.
                item = EventItem()
                item['desc'] = "TBA"
                item['title'] = event.select('.//h4[contains(@class, "loading")]/text()').extract()[0]
                item['link'] = event.select('./a/@href').extract()[0]
                item['location'] = "TBA"
                item['eventdate'] = event.select('.//p[contains(@class, "muted")]/text()').extract()[0]
                item['cat'] = "events"

                #print unicode(item['title']).encode('utf8')
                self.item_cnt += 1
                yield item

        # try to parse the next page
        try:
            nextPageLink = hxs.select('//div[contains(@class, "simple-infinite-pager")]/a/@href').extract()[0]
            nextPageLink = urlparse.urljoin(response.url, nextPageLink)
            self.log("Moving onto next page: link is %s" % nextPageLink)
            yield Request(nextPageLink, callback = self.parse)
        except:
            self.log("I have reached the last page... total items is %d" % self.item_cnt)

        
        
        
