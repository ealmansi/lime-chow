import scrapy
from dateparser import parse as parse_date
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils

class ComedyCafeBerlinSpider(scrapy.Spider):
    name = "comedy_cafe_berlin"
    allowed_domains = ["comedycafeberlin.com"]
    start_urls = ["https://www.comedycafeberlin.com/schedule/"]

    def parse(self, response):
        for event_url in response.css(
            ".tribe-events-pro-photo__event-title-link::attr(href)"
        ).extract():
            yield scrapy.Request(url=event_url, callback=self.parse_event)

    def parse_event(self, response):
        venue = self.name
        date = self.get_event_date(response)
        title = response.css(
            ".tribe-events-single-event-title::text"
        ).extract_first().strip()
        url = response.url
        thumbnail_url = response.css(
            ".tribe-events-event-image img::attr(src)"
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

    def get_event_date(self, response):
        text = response.css(
            ".tribe-events-schedule__date::text"
        ).extract_first().strip()
        return parse_date(text).strftime("%d/%m/%y")
