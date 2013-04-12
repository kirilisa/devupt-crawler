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
    blurb = Field()
    src = Field()
    pass

class ProjectItem(Item):
    title = Field()    
    link = Field()
    blurb = Field()
    lang = Field()    
    updated = Field()
    stars = Field()
    forks = Field()
    src = Field()

class CourseItem(Item):
    title = Field()    
    link = Field()    
    blurb = Field()
    school = Field()
    school_link = Field()
    course_date = Field()
    course_length = Field()
    src = Field()

class EventItem(Item):    
    title = Field()    
    link = Field()    
    blurb = Field()
    host = Field()    
    location = Field()
    event_date = Field()
    event_time = Field()
    src = Field()
