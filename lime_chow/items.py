import scrapy

class LimeChowItem(scrapy.Item):
    id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field()
    thumbnail_url = scrapy.Field()
    extracted_at = scrapy.Field()
