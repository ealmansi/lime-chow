from datetime import datetime
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils
import pytz
import scrapy
import validators


class MadameClaudeSpider(scrapy.Spider):
    name = "madame_claude"
    allowed_domains = ["madameclaude.de"]
    start_urls = ["https://madameclaude.de/events/"]

    def parse(self, response):
        for event_url in response.xpath(
            "".join(
                [
                    "//article",
                    "//div[contains(@class, 'title')]",
                    "//a",
                    "/@href",
                ]
            )
        ).extract():
            yield scrapy.Request(url=event_url, callback=self.parse_event)

    def parse_event(self, response):
        venue = self.name
        starts_on, starts_at = self.parse_starts_on(response)
        title = response.xpath(
            "".join(
                [
                    "//article",
                    "//h2",
                    "/text()",
                ]
            )
        ).extract_first()
        url = response.url
        thumbnail_url = response.xpath(
            "".join(
                [
                    "//article",
                    "//img",
                    "/@src",
                ]
            )
        ).extract_first()
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
        date = response.css(
            " ".join(
                [
                    ".primary-info-single-event",
                    ".date",
                    ".numbers",
                    "font::text",
                ]
            )
        ).extract_first()
        assert date is not None
        info = response.css(
            " ".join(
                [
                    ".primary-info-single-event",
                    ".info",
                    "p::text",
                ]
            )
        ).extract_first()
        assert info is not None
        [_, start, _] = info.split(" / ")
        time = start[len("Start ") :]
        starts_at = date.strip() + " " + time.strip()
        starts_at = datetime.strptime(starts_at, "%d/%m/%y %H:%M")
        starts_at = starts_at.astimezone(pytz.timezone("Europe/Berlin"))
        starts_on = str(starts_at.date())
        starts_at = starts_at.isoformat()
        return starts_on, starts_at

    def parse_links(self, response):
        links = response.xpath(
            "".join(
                [
                    "//article",
                    "//div[contains(@class, 'info')]",
                    "//a",
                    "/@href",
                ]
            )
        ).extract()
        links = list(filter(validators.url, links))
        links = links[:10]
        return links
