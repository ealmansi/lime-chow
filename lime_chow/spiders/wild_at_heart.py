import scrapy
import re
from datetime import datetime
from lime_chow.items import LimeChowItem


class WildAtHeartSpider(scrapy.Spider):
    name = "wild_at_heart"
    allowed_domains = ["wildatheartberlin.de"]
    start_urls = ["http://wildatheartberlin.de/concerts.php"]

    def parse(self, response):
        for event in response.xpath(
            "//tr"
        ):
            title = self.get_event_title(event)
            datum = event.xpath(
                ".//span[contains(@class, 'datum')]/text()"
            ).extract()
            date = datum[1].replace(".", "/") + "23"
            yield LimeChowItem(
                id = (
                    "wild-at-heart-" + re.sub("[^a-z0-9]+", "-", date + "-" + title.lower()).strip("-")
                )[:80],
                venue = self.name,
                url = response.url,
                title = title,
                date = date,
                thumbnail_url = "http://wildatheartberlin.de" + event.xpath(
                    ".//img/@src"
                ).extract_first(),
                extracted_at = datetime.now().isoformat()
            )

    def get_event_title(self, event):
        title_chunks = []
        headlines = event.xpath(
            ".//td[2]//p[contains(@class, 'headlines')]/text()"
        ).extract()
        for headline in headlines:
            title_chunks.append(headline.strip('"').strip())
        bands = event.xpath(
            ".//td[2]//span[contains(@class, 'band')]/text()"
        ).extract()
        for band in bands:
            title_chunks.append(band.strip('"').strip())
        support_bands = event.xpath(
            ".//td[2]//span[contains(@class, 'support_band')]/text()"
        ).extract()
        for support_band in support_bands:
            title_chunks.append(support_band.strip('"').strip())
        return " - ".join(title_chunks)
