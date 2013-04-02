from scrapy.contrib.spiders import XMLFeedSpider
from devupt import utils

from devupt.items import NewsItem
import re

class TechmemeSpider(XMLFeedSpider):
    name = "techmeme"
    #allowed_domains = ["techmeme.com"]
    start_urls = ["http://www.techmeme.com/feed.xml"]
    itertag = 'item'

    def parse_node(self, response, node):        
        data = node.select('./description/text()').extract()[0]

        # this is a terrible regex
        match = re.search(r'<SPAN[^>]+>.*?<A HREF="([^"]+)">(.*?)</A>.*?</SPAN>(.*?)</P>', data, re.DOTALL)
        if match:
            item = NewsItem()
            item['title'] = match.group(2)
            item['link'] = match.group(1)
            item['desc'] = match.group(3)
            item['cat'] = "news"

            return item        

        

