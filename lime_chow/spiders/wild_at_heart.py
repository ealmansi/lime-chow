import scrapy
import urllib.parse
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils

class WildAtHeartSpider(scrapy.Spider):
    name = "wild_at_heart"
    allowed_domains = ["wildatheartberlin.de"]
    start_urls = ["http://wildatheartberlin.de/concerts.php"]

    def parse(self, response):
        for event in response.xpath("//tr"):
            venue = self.name
            date = self.get_event_date(event)
            title = self.get_event_title(event)
            url = response.url
            thumbnail_url = self.get_event_thumbnail_url(event)
            yield EventItem(
                id = EventUtils.build_id(venue, date, title),
                extracted_at = EventUtils.get_current_datetime(),
                venue = venue,
                date = date,
                title = title,
                url = url,
                thumbnail_url = thumbnail_url,
                links = [],
            )

    def get_event_title(self, event):
        title_chunks = []
        headlines = event.xpath("".join([
            ".",
            "//td[2]",
            "//p[contains(@class, 'headlines')]",
            "/text()",
        ])).extract()
        for headline in headlines:
            title_chunks.append(headline.strip('"').strip())
        bands = event.xpath("".join([
            ".",
            "//td[2]",
            "//span[contains(@class, 'band')]",
            "/text()",
        ])).extract()
        for band in bands:
            title_chunks.append(band.strip('"').strip())
        support_bands = event.xpath("".join([
            ".",
            "//td[2]",
            "//span[contains(@class, 'support_band')]",
            "/text()",
        ])).extract()
        for support_band in support_bands:
            title_chunks.append(support_band.strip('"').strip())
        return " - ".join(title_chunks)

    def get_event_date(self, event):
        datum = event.xpath("".join([
            ".",
            "//span[contains(@class, 'datum')]",
            "/text()",
        ])).extract()
        date_prefix = datum[1]
        # TODO: Fix year
        return date_prefix.replace(".", "/") + "23"

    def get_event_thumbnail_url(self, event):
        img_src = event.xpath("".join([
            ".",
            "//img",
            "/@src",
        ])).extract_first()
        # Use wsrv.nl to work around non-https img sources.
        return "https://wsrv.nl/?url=" + urllib.parse.quote(
            "wildatheartberlin.de" + img_src
        )
