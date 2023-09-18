import scrapy
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils

class SchokoladenSpider(scrapy.Spider):
    name = "schokoladen"
    allowed_domains = ["schokoladen-mitte.de"]
    start_urls = ["https://schokoladen-mitte.de/"]

    def parse(self, response):
        for event in response.css(".event"):
            venue = self.name
            date = self.get_event_date(event)
            title = event.xpath("".join([
                ".",
                "//div[contains(@class, 'title')]",
                "//div",
                "/text()",
            ])).extract_first().strip()
            url = event.xpath("".join([
                ".",
                "//a[contains(@class, 'ticketlink')]",
                "/@href",
            ])).extract_first() or response.url
            thumbnail_url = "https://www.schokoladen-mitte.de" + (
                event.xpath("".join([
                    ".",
                    "//div[contains(@class, 'imageWrapper')]",
                    "//img",
                    "/@src",
                ])).extract_first() or
                event.xpath("".join([
                    ".",
                    "//div[contains(@class, 'carousel-item')]",
                    "//img",
                    "/@src",
                ])).extract_first()
            )
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
        date_prefix = event.xpath("".join([
            ".",
            "//div[contains(@class, 'eventHeader')]",
            "//div[contains(@class, 'subHeader')]",
            "//span[2]",
            "/text()",
        ])).extract_first()
        # TODO: Fix year
        return date_prefix.replace(".", "/") + "23"
