from datetime import datetime
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils
import pytz
import re
import scrapy
import validators


class ClashSpider(scrapy.Spider):
    name = "clash"
    allowed_domains = ["clash-berlin.de"]
    start_urls = ["https://clash-berlin.de/"]

    def parse(self, response):
        for event in response.css(".gigs-container .item"):
            venue = self.name
            starts_on, starts_at = self.parse_starts_on(event)
            title = event.css(".gig-title::text").extract_first()
            assert title is not None
            title = title.strip()
            url = response.url
            thumbnail_url = event.css(".flyer img::attr(src)").extract_first()
            links = self.parse_links(event)
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

    def parse_starts_on(self, event):
        date = event.css(".dateTwo::text").extract_first()
        assert date is not None
        time = "".join(event.css(".time::text").extract())
        starts_at = date.strip() + " " + re.sub(r"\t+", " ", time).strip()
        starts_at = datetime.strptime(starts_at, "%d.%m.%y %a %H:%M")
        starts_at = starts_at.astimezone(pytz.timezone("Europe/Berlin"))
        starts_on = str(starts_at.date())
        starts_at = starts_at.isoformat()
        return starts_on, starts_at

    def parse_links(self, event):
        links = event.css(".info-extra a::attr(href)").extract()
        links = list(filter(validators.url, links))
        links = links[:10]
        return links
