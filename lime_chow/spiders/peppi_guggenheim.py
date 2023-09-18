import scrapy
import validators
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils

class PeppiGuggenheimSpider(scrapy.Spider):
    name = "peppi_guggenheim"
    allowed_domains = ["peppi-guggenheim.de"]
    start_urls = ["https://www.peppi-guggenheim.de/?post_type=tribe_events"]

    def parse(self, response):
        for event_url in response.css(
            ".tribe-events-calendar-list__event-title-link::attr(href)"
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

    def get_event_date(self, response):
        abbr = response.xpath("".join([
            ".",
            "//abbr",
            "/@title",
        ])).extract_first()
        return "/".join(abbr[2:].split("-")[::-1])

    def get_event_links(self, response):
        links = response.css(
            ".tribe-events-single-event-description a::attr(href)"
        ).extract()
        links = list(filter(validators.url, links))
        links = links[:10]
        return links
