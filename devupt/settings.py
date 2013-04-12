# Scrapy settings for devupt project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'devupt'

SPIDER_MODULES = ['devupt.spiders']
NEWSPIDER_MODULE = 'devupt.spiders'

ITEM_PIPELINES = [
    'devupt.pipelines.CleanerPipeline',
    'devupt.pipelines.DuplicateLinksPipeline',
    'devupt.pipelines.DBWriterPipeline',
    #'devupt.pipelines.JsonWriterPipeline',
]

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'devupt (+http://www.devupt.com)'
