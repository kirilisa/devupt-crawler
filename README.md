devupt-crawler
==============

This is a custom crawler for devUpt: it uses the Scrapy framework (http://scrapy.org). 

You must have Scrapy installed on your machine for this code to work. Please see http://doc.scrapy.org/en/latest/intro/install.html.

A brief intro to Scrapy can be found here: http://doc.scrapy.org/en/latest/intro/overview.html.

A Scrapy basic tutorial can be found here: http://http://doc.scrapy.org/en/latest/intro/tutorial.html. 

Once you have it all installed, you would do as follows to run the techmeme crawler and save the results to items.json
- cd into the devupt directory
- scrapy crawl techmeme -o items.json -t json