#from scrapy.spider import BaseSpider
#from scrapy.selector import XmlXPathSelector
from scrapy.contrib.spiders import XMLFeedSpider
from scrapy import log

from devupt.items import NewsItem
import re

class TechmemeSpider(XMLFeedSpider):
    name = "techmeme"
    #allowed_domains = ["techmeme.com"]
    start_urls = ["http://www.techmeme.com/feed.xml"]
    itertag = 'item'
    items = []

    def parse_node(self, response, node):        
        data = node.select('./description/text()').extract()[0]

        # this is a terrible regex
        match = re.search(r'<SPAN[^>]+>.*?<A HREF="([^"]+)">(.*?)</A>.*?</SPAN>(.*?)</P>', data, re.DOTALL)
        if match:
            item = NewsItem()
            item['title'] = match.group(2)
            item['link'] = match.group(1)
            item['desc'] = match.group(3)

            self.items.append(item)            
            return item        

    # this is called every time parse_node is finished with a node
    def process_results(self, response, results):
        self.log("We are finished!! Got %s items." % len(self.items))        
        for item in results:
            self.log("iterating through results... %s" % item['title'])
        # now enter items into DB? Or better to do it individually above?
        return results
        

