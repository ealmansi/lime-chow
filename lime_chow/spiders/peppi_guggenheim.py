from datetime import datetime
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils
import pytz
import scrapy
import validators


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
        starts_on, starts_at = self.parse_starts_on(response)
        title = (
            response.css(".tribe-events-single-event-title::text")
            .extract_first()
            .strip()
        )
        url = response.url
        thumbnail_url = (
            response.css(".tribe-events-event-image img::attr(src)")
            .extract_first()
            .strip()
        )
        links = self.parse_links(response)
        yield EventItem(
            id=EventUtils.build_event_id(venue, starts_on, title),
            venue=venue,
            starts_on=starts_on,
            starts_at=starts_at,
            title=title,
            url=url,
            thumbnail_url=thumbnail_url,
            links=links,
            extracted_at=datetime.now().isoformat(),
        )

    def parse_starts_on(self, response):
        date = response.css(".tribe-events-start-date::attr(title)").extract_first()
        assert date is not None
        time = response.css(".tribe-events-start-time::text").extract_first()
        assert time is not None
        starts_at = date.strip() + " " + time.strip()[: len("hh:mm")]
        starts_at = datetime.strptime(starts_at, "%Y-%m-%d %H:%M")
        starts_at = starts_at.astimezone(pytz.timezone("Europe/Berlin"))
        starts_on = str(starts_at.date())
        starts_at = starts_at.isoformat()
        return starts_on, starts_at

    def parse_links(self, response):
        links = response.css(
            ".tribe-events-single-event-description a::attr(href)"
        ).extract()
        links = list(filter(validators.url, links))
        links = links[:10]
        return links
