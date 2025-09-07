from datetime import datetime, timedelta

import pytz
from icalevents import icalevents
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils
import scrapy
import time
from parsel import Selector
import validators


class PeppiGuggenheimSpider(scrapy.Spider):
    name = "peppi_guggenheim"
    allowed_domains = ["example.com"]
    start_urls = ["https://www.example.com"]

    def parse(self, _):
        url = "https://calendar.google.com/calendar/ical/jn2h4trf1n3u3ug4mh9vk1c0s4@group.calendar.google.com/public/basic.ics"
        start_date = datetime.now()
        end_date = datetime.now() + timedelta(days=30)
        events = icalevents.events(url, start=start_date, end=end_date)
        for event in events:
            venue = self.name
            starts_on = event.start.astimezone(pytz.timezone("Europe/Berlin"))
            starts_at = starts_on.replace(
                hour=20, minute=0, second=0, microsecond=0
            ).isoformat()
            starts_on = str(starts_on.date())
            title = event.summary
            links = Selector(text=event.description).css("a::attr(href)").getall()
            links = list(filter(validators.url, links))
            links = links[:10]
            yield EventItem(
                id=EventUtils.build_event_id(venue, starts_on, title),
                venue=venue,
                starts_on=starts_on,
                starts_at=starts_at,
                title=title,
                url="https://peppi-guggenheim.de/",
                thumbnail_url="https://peppi-guggenheim.de/file/i/6d6433a3440361412.jpg",
                links=links,
                extracted_at=datetime.now().isoformat(),
                ttl=int(time.time() + 36 * 3600),
            )
