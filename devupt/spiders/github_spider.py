from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from devupt import utils
from devupt.items import ProjectItem
import urlparse
import re
import sys

class GithubSpider(BaseSpider):
    name = "github"
    allowed_domains = ["github.com"]
    start_urls = [
        "http://www.github.com/search?q=stars%3A%3A%3E5000&type=Repositories&s=stars"
        ]
    item_cnt = 0

    def parse(self, response):
        utils.devlog('Parsing page... depth is %s' % response.meta['depth'])
        
        # grab info from projects on this page
        #@@@ stars and forks do not work!
        hxs = HtmlXPathSelector(response)        
        for project in hxs.select('//li[contains(@class, "public")]'):
            item = ProjectItem()
            item['blurb'] = "" if not project.select('.//p[contains(@class, "description")]/text()').extract() else project.select('.//p[contains(@class, "description")]/text()').extract()[0]
            item['title'] = project.select('./h3/a/text()').extract()[0]
            item['link'] = urlparse.urljoin("https://github.com", project.select('./h3/a/@href').extract()[0])
            item['lang'] = project.select('./ul/li[1]/text()').extract()[0]
            item['updated'] = project.select('.//p[contains(@class, "updated-at")]/time/@title').extract()[0]
            item['stars'] = project.select('.//li[contains(@class, "stargazers")]/a/@href').extract()[0]
            item['forks'] = project.select('.//li[contains(@class, "forks")]/a/text()').extract()[0]
            item['src'] = "projects"
            print "\nNUM STARS: %s" % item['stars']
            sys.exit(1)
            if item['stars'] == 0:
                print "NO STARS!!!!!!!! (%s)" % item['stars']
                sys.exit(1)                

            #print unicode(item['title']).encode('utf8')
            self.item_cnt += 1
            yield item

        # try to parse the next page
        try:
            nextPageLink = hxs.select('//div[contains(@class, "pagination")]/a[contains(@class, "next_page")]/@href').extract()[0]
            nextPageLink = urlparse.urljoin(response.url, nextPageLink)
            utils.devlog("Moving onto next page: link is %s" % nextPageLink)
            yield Request(nextPageLink, callback = self.parse)
        except:
            utils.devlog("I have reached the last page... total items is %d" % self.item_cnt)

        
        
        
