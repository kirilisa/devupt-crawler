from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from devupt.items import EventItem
from devupt import utils
import urlparse
import re
from datetime import datetime
from datetime import timedelta

class MeetupSpider(BaseSpider):
    name = "meetup"
    #allowed_domains = ["meetup.com"]
    start_urls = [
        "http://www.meetup.com/find/?offset=0&psize=64&currentpage=1&categories=34&radius=10&userFreeform=San+Francisco&events=true&sort=default" # tech category 34
        ]
    item_cnt = 0

    def parse(self, response):                
        depth = response.meta['depth']
        utils.devlog('depth is %s' % depth)

        # when to quit!!
        if depth > 60:
            utils.devlog("I have crawled enough pages... total items is %d" % self.item_cnt)
            return

        # generate a cutoff date so we don't search for meetups in the distant future
        now = datetime.now()
        cutoff = now + timedelta(weeks=12)
        utils.devlog("The cutoff date is %s" % cutoff.strftime("%B %d, %Y"))

        # grab info from events on this page
        hxs = HtmlXPathSelector(response)        
        for event in hxs.select('//ul[contains(@class, "event-listing-container")]/li[contains(@class, "event-listing")]'):
            # stop at cutoff date so we don't get too many
            date = datetime(int(event.select('@data-year').extract()[0]), int(event.select('@data-month').extract()[0]), int(event.select('@data-day').extract()[0]))
            if date > cutoff:
                utils.devlog("I have reached the cutoff date... total items is %d" % self.item_cnt)
                return

            # not yet in use - pages are not standardized enough!            
            #link = event.select('./a[contains(@class, "list-time")]/@href').extract()[0]
            #yield Request(link, callback = self.parseItem)
            item = EventItem()            
            item['link'] = event.select('./a[contains(@class, "list-time")]/@href').extract()[0]
            item['eventdate'] = date.strftime("%B %d, %Y")
            item['eventtime'] = event.select('./a[contains(@class, "list-time")]/text()').extract()[0] 
            item['host'] = event.select('./div/a[contains(@class, "chapter-name")]/text()').extract()[0]
            item['title'] = event.select('./div/h4/a[contains(@class, "event-title")]/text()').extract()[0]
            item['desc'] = ""                                
            item['location'] = "TBA"
            item['cat'] = "events"
            self.item_cnt += 1
            yield item
            
        # try to parse the next page
        # There is a bug on the meetup site such that the Next link in the HTML is wrong.
        # Therefore I am generating the crawl link manually.
        try:
            p = re.compile('currentpage=([0-9]+)')
            currentPage = int(p.search(response.url).group(1))
            nextPage = currentPage + 1;
            offset = currentPage * 64
            nextPageLink = "http://www.meetup.com/find/?offset=%s&psize=64&currentpage=%s&categories=34&radius=10&userFreeform=San+Francisco&events=true&sort=default" % (offset, nextPage)
                        
            #nextPageLink = hxs.select('//div[contains(@class, "simple-infinite-pager")]/a/@href').extract()[0]
            #nextPageLink = urlparse.urljoin(response.url, nextPageLink)
            utils.devlog("Moving onto next page: offset is %s and nextpage is %s which yields link %s" % (offset, nextPage, nextPageLink))
            yield Request(nextPageLink, callback = self.parse)
        except:
            utils.devlog("Failed to fetch next page to crawl... total items is %d" % self.item_cnt)

    # not yet in use - pages are not standardized enough!
    # thus I'm not convinced doing this is worth it just for location and description
    def parseItem(self, response):
        utils.devlog("Beginning on new item...")

        hxs = HtmlXPathSelector(response)        
        item = EventItem()
        item['link'] = response.url
        item['title'] = hxs.select('//div[contains(@id, "event-title")]/@data-name').extract()[0]
        item['eventdate'] = "BLAH" if not hxs.select('//div[contains(@id, "event-content")]//li[contains(@id, "event-when")]//time[contains(@id, "event-start-time")]/p[1]/text()').extract() else "HAPPY"
        #item['location'] = hxs.select('//div[contains(@id, "event-content")]//li[contains(@id, "event-where")]/@data-name').extract()[0]
        #item['location'] += hxs.select('//div[contains(@id, "event-content")]//li[contains(@id, "event-where")]/@data-address').extract()[0]
        #item['desc'] += hxs.select('//div[contains(@id, "event-content")]//li[contains(@id, "event-desc")]//p/text()').extract()[0]
        #item['host'] = hxs.select('//div/a[contains(@class, "chapter-name")]/text()').extract()[0]
        item['cat'] = "events"
        
        self.item_cnt += 1
        yield item

        
        
        
