from datetime import datetime
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils
import pytz
import scrapy
import validators


class LoopholeSpider(scrapy.Spider):
    name = "loophole"
    allowed_domains = ["loophole.berlin"]
    start_urls = ["https://loophole.berlin"]

    def parse(self, response):
        for event_url in response.css(".excerpt-title a::attr(href)").extract():
            yield scrapy.Request(url=event_url, callback=self.parse_event)

    def parse_event(self, response):
        venue = self.name
        starts_on = self.parse_starts_on(response)
        title = response.css(".entry-title::text").extract_first()
        assert title is not None
        title = title.strip()
        url = response.url
        thumbnail_url = response.css(".featured-image::attr(style)").extract_first()
        assert thumbnail_url is not None
        thumbnail_url = thumbnail_url.strip()[len("background-image: url(") : -len(")")]
        links = self.parse_links(response)
        yield EventItem(
            id=EventUtils.build_event_id(venue, starts_on, title),
            venue=venue,
            starts_on=starts_on,
            title=title,
            url=url,
            thumbnail_url=thumbnail_url,
            links=links,
            extracted_at=datetime.now().isoformat(),
        )

    def parse_starts_on(self, event):
        date = event.css(".date::text").extract_first()
        assert date is not None
        starts_on = datetime.strptime(date.strip(), "%d/%m/%Y")
        starts_on = pytz.timezone("Europe/Berlin").localize(starts_on)
        starts_on = str(starts_on.date())
        return starts_on

    def parse_links(self, response):
        links = response.css(".entry-content a::attr(href)").extract()
        links = list(filter(validators.url, links))
        links = links[:10]
        return links
