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
        for event_url in event_urls:
            yield scrapy.Request(url=event_url, callback=self.parse_event)

    def parse_event(self, response):
        venue = self.name
        starts_on, starts_at = self.parse_starts_on(response)
        title = response.css(".wp-block-heading::text").extract_first().strip()
        url = response.url
        thumbnail_url = (
            response.css(".wp-block-kadence-image img::attr(src)")
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
        starts_at = datetime.strptime(starts_at, "%A, %B %d %I:%M%p")
        starts_at = pytz.timezone("Europe/Berlin").localize(starts_at)
        starts_at = self.guess_year(starts_at)
        starts_on = str(starts_at.date())
        starts_at = starts_at.isoformat()
        return starts_on, starts_at

    def guess_year(self, starts_at):
        now = pytz.timezone("Europe/Berlin").localize(datetime.now())
        starts_at_prev = starts_at.replace(year=now.year - 1)
        starts_at_curr = starts_at.replace(year=now.year)
        starts_at_next = starts_at.replace(year=now.year + 1)
        best = None
        diff = None
        for candidate in [starts_at_prev, starts_at_curr, starts_at_next]:
            if best is None or abs(candidate - now) < diff:
                best = candidate
                diff = abs(candidate - now)
        assert best is not None
        return best
