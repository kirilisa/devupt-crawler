from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import XmlXPathSelector

from devupt.items import NewsItem
import re

class TechmemeSpider(BaseSpider):
    name = "techmeme"
    allowed_domains = ["techmeme.com"]
    start_urls = [
        #"http://www.techmeme.com",
        "http://www.techmeme.com/feed.xml"
        ]
    
    def parse(self, response):
        xxs = XmlXPathSelector(response)
        sites = xxs.select('//item/description')
        print("I got %s items " % len(sites))

        items = []        
        for site in sites:
            item = NewsItem()
            data = "".join(site.select('text()').extract());

            # this is a terrible regex
            match = re.search(r'<SPAN[^>]+>.*?<A HREF="([^"]+)">(.*?)</A>.*?</SPAN>(.*?)</P>', data, re.DOTALL)
            if match:
                #print "\r\nI have found %s" % match.group(3)
                item['desc'] = match.group(3)
                item['title'] = match.group(2)
                item['link'] = match.group(1)
                items.append(item)
            
        return items
