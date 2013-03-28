from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from scrapy import log
from devupt.items import ProjectItem
import urlparse
import re

class GithubSpider(BaseSpider):
    name = "github"
    allowed_domains = ["github.com"]
    start_urls = [
        "http://www.github.com/search?q=stars%3A%3A%3E5000&type=Repositories&s=stars"
        ]
    items = []

    def parse(self, response):
        self.log('Parsing page... depth is %s' % response.meta['depth'])
        
        # grab info from projects on this page
        hxs = HtmlXPathSelector(response)        
        for project in hxs.select('//li[contains(@class, "public")]'):
            item = ProjectItem()
            item['desc'] = "".join(project.select('.//p[contains(@class, "description")]/text()').extract())
            item['title'] = "".join(project.select('./h3/a/text()').extract())
            item['link'] = "https://github.com" + "".join(project.select('./h3/a/@href').extract())
            item['language'] = "".join(project.select('./ul/li[1]/text()').extract())
            item['updated'] = "".join(project.select('.//p[contains(@class, "updated-at")]/time/text()').extract())
            item['stars'] = "".join(project.select('.//li[contains(@class, "stargazers")]/a/text()').extract())
            item['forks'] = "".join(project.select('.//li[contains(@class, "forks")]/a/text()').extract())

            #print unicode(item['title']).encode('utf8')
            self.items.append(item)

        # try to parse the next page
        try:
            nextPageLink = hxs.select('//div[contains(@class, "pagination")]/a[contains(@class, "next_page")]/@href').extract()[0]
            nextPageLink = urlparse.urljoin(response.url, nextPageLink)
            self.log("Moving onto next page: link is %s" % nextPageLink)
            yield Request(nextPageLink, callback = self.parse)
        except:
            self.log("I have reached the last page... total items is %s" % len(self.items))
            # now enter items into DB? Or better to do it individually above?

        
