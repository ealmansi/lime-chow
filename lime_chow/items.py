import scrapy


class EventItem(scrapy.Item):
    id = scrapy.Field()
    venue = scrapy.Field()
    starts_on = scrapy.Field()
    starts_at = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    thumbnail_url = scrapy.Field()
    links = scrapy.Field()
    extracted_at = scrapy.Field()
    ttl = scrapy.Field()
