import scrapy
import re
from datetime import datetime
from lime_chow.items import LimeChowItem


class SchokoladenSpider(scrapy.Spider):
    name = "schokoladen"
    allowed_domains = ["schokoladen-mitte.de"]
    start_urls = ["https://schokoladen-mitte.de/"]

    def parse(self, response):
        for event in response.css(
            ".event"
        ):
            title = event.xpath(
                ".//div[contains(@class, 'title')]//div/text()"
            ).extract_first().strip()
            date = event.xpath(
                ".//div[contains(@class, 'eventHeader')]//div[contains(@class, 'subHeader')]//span[2]/text()"
            ).extract_first().replace(".", "/") + "23" # TODO: Fix year
            yield LimeChowItem(
                id = (
                    "schokoladen-" + re.sub("[^a-z0-9]+", "-", date + "-" + title.lower()).strip("-")
                )[:80],
                url = event.xpath(
                    ".//a[contains(@class, 'ticketlink')]/@href"
                ).extract_first() or response.url,
                title = title,
                date = date,
                thumbnail_url = "https://www.schokoladen-mitte.de" + (
                    event.xpath(
                        ".//div[contains(@class, 'imageWrapper')]//img/@src"
                    ).extract_first() or
                    event.xpath(
                        ".//div[contains(@class, 'carousel-item')]//img/@src"
                    ).extract_first()
                ),
                extracted_at = datetime.now().isoformat()
            )
