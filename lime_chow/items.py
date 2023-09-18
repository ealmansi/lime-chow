import scrapy

class EventItem(scrapy.Item):
    id = scrapy.Field()
    extracted_at = scrapy.Field()
    venue = scrapy.Field()
    date = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    thumbnail_url = scrapy.Field()
    links = scrapy.Field()
