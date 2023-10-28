import time
from datetime import datetime
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils
import pytz
import scrapy


class ComedyCafeBerlinSpider(scrapy.Spider):
    name = "comedy_cafe_berlin"
    allowed_domains = ["comedycafeberlin.com"]
    start_urls = ["https://www.comedycafeberlin.com/schedule/"]

    def parse(self, response):
        event_urls = response.css(
            ".tribe-events-pro-photo__event-title-link::attr(href)"
        ).extract()
        self.logger.info("parse response.url %s", response.url)
        self.logger.info("parse response.text %s", response.text)
        self.logger.info("parse event_urls %s", ", ".join(event_urls))
        for event_url in event_urls:
            yield scrapy.Request(url=event_url, callback=self.parse_event)

    def parse_event(self, response):
        self.logger.info("parse_event response.url %s", response.url)
        self.logger.info("parse_event response.text %s", response.text)
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
        yield EventItem(
            id=EventUtils.build_event_id(venue, starts_on, title),
            venue=venue,
            starts_on=starts_on,
            starts_at=starts_at,
            title=title,
            url=url,
            thumbnail_url=thumbnail_url,
            links=[],
            extracted_at=datetime.now().isoformat(),
            ttl=int(time.time() + 36 * 3600),
        )

    def parse_starts_on(self, response):
        date = response.css(".tribe-events-schedule__date--start::text").extract_first()
        assert date is not None
        time = response.css(".tribe-events-schedule__time--start::text").extract_first()
        assert time is not None
        starts_at = date.strip() + " " + time.strip()
        starts_at = datetime.strptime(starts_at, "%A, %B %d, %Y %I:%M%p")
        starts_at = pytz.timezone("Europe/Berlin").localize(starts_at)
        starts_on = str(starts_at.date())
        starts_at = starts_at.isoformat()
        return starts_on, starts_at
