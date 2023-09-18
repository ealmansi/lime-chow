import scrapy
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils

class LoopholeSpider(scrapy.Spider):
    name = "loophole"
    allowed_domains = ["loophole.berlin"]
    start_urls = ["http://loophole.berlin"]

    def parse(self, response):
        for event in response.css(".post"):
            venue = self.name
            date = self.get_event_date(event)
            title = event.css(
                ".excerpt-title a::text"
            ).extract_first().strip()
            url = event.css(
                ".excerpt-title a::attr(href)"
            ).extract_first().strip()
            thumbnail_url = event.css(
                ".featured-image::attr(data-background)"
            ).extract_first().strip()
            yield EventItem(
                id = EventUtils.build_id(venue, date, title),
                extracted_at = EventUtils.get_current_datetime(),
                venue = venue,
                date = date,
                title = title,
                url = url,
                thumbnail_url = thumbnail_url,
                links = [],
            )

    def get_event_date(self, event):
        date_long = event.css("span.date::text").extract_first()
        [day, month, year] = date_long.split("/")
        return "/".join([day, month, year[2:]])
