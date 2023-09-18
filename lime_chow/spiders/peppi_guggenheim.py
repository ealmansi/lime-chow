import scrapy
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils

class PeppiGuggenheimSpider(scrapy.Spider):
    name = "peppi_guggenheim"
    allowed_domains = ["peppi-guggenheim.de"]
    start_urls = ["https://www.peppi-guggenheim.de/?post_type=tribe_events"]

    def parse(self, response):
        for event in response.css(".tribe-events-calendar-list__event-row"):
            venue = self.name
            date = self.get_event_date(event)
            title = event.css(
                ".tribe-events-calendar-list__event-title-link::text"
            ).extract_first().strip()
            url = event.css(
                ".tribe-events-calendar-list__event-title-link::attr(href)"
            ).extract_first().strip()
            thumbnail_url = event.css(
                ".tribe-events-calendar-list__event-featured-image::attr(src)"
            ).extract_first().strip()
            yield EventItem(
                id = EventUtils.build_id(venue, date, title),
                extracted_at = EventUtils.get_current_datetime(),
                venue = venue,
                date = date,
                title = title,
                url = url,
                thumbnail_url = thumbnail_url,
            )

    def get_event_date(self, event):
        datetime = event.xpath("".join([
            ".",
            "//time",
            "/@datetime",
        ])).extract_first()
        return "/".join(datetime[2:].split("-")[::-1])
