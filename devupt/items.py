# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class DevuptItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass

class NewsItem(Item):
    title = Field()
    link = Field()
    desc = Field()
    pass

class ProjectItem(Item):
    title = Field()    
    link = Field()
    language = Field()
    desc = Field()
    updated = Field()
    stars = Field()
    forks = Field()
