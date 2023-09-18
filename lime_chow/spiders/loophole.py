import scrapy
import validators
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils

class LoopholeSpider(scrapy.Spider):
    name = "loophole"
    allowed_domains = ["loophole.berlin"]
    start_urls = ["http://loophole.berlin"]

    def parse(self, response):
        for event_url in response.css(
            ".excerpt-title a::attr(href)"
        ).extract():
            yield scrapy.Request(url=event_url, callback=self.parse_event)

    def parse_event(self, response):
        venue = self.name
        date = self.get_event_date(response)
        title = response.css(
            ".entry-title::text"
        ).extract_first().strip()
        url = response.url
        thumbnail_url = response.css(
            ".featured-image::attr(style)"
        ).extract_first().strip()
        thumbnail_url = thumbnail_url[len("background-image: url("):-len(")")]
        links = self.get_event_links(response)
        yield EventItem(
            id = EventUtils.build_id(venue, date, title),
            extracted_at = EventUtils.get_current_datetime(),
            venue = venue,
            date = date,
            title = title,
            url = url,
            thumbnail_url = thumbnail_url,
            links = links,
        )

    def get_event_date(self, event):
        date_long = event.css("span.date::text").extract_first()
        [day, month, year] = date_long.split("/")
        return "/".join([day, month, year[2:]])

    def get_event_links(self, response):
        links = response.css(
            ".entry-content a::attr(href)"
        ).extract()
        links = list(filter(validators.url, links))
        links = links[:10]
        return links
