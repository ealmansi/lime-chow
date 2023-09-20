from datetime import datetime
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils
import pytz
import scrapy
import urllib.parse
import validators


class WildAtHeartSpider(scrapy.Spider):
    name = "wild_at_heart"
    allowed_domains = ["wildatheartberlin.de"]
    start_urls = ["http://wildatheartberlin.de/concerts.php"]

    def parse(self, response):
        for event in response.xpath("//tr"):
            venue = self.name
            starts_on = self.parse_starts_on(event)
            title = self.parse_title(event)
            url = response.url
            thumbnail_url = self.parse_thumbnail_url(event)
            links = self.parse_links(event)
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

    def parse_title(self, event):
        title_chunks = []
        headlines = event.xpath(
            "".join(
                [
                    ".",
                    "//td[2]",
                    "//p[contains(@class, 'headlines')]",
                    "/text()",
                ]
            )
        ).extract()
        for headline in headlines:
            title_chunks.append(headline.strip('"').strip())
        bands = event.xpath(
            "".join(
                [
                    ".",
                    "//td[2]",
                    "//span[contains(@class, 'band')]",
                    "/text()",
                ]
            )
        ).extract()
        for band in bands:
            title_chunks.append(band.strip('"').strip())
        support_bands = event.xpath(
            "".join(
                [
                    ".",
                    "//td[2]",
                    "//span[contains(@class, 'support_band')]",
                    "/text()",
                ]
            )
        ).extract()
        for support_band in support_bands:
            title_chunks.append(support_band.strip('"').strip())
        return " - ".join(title_chunks)

    def parse_starts_on(self, event):
        [_, date_without_year, *_] = event.xpath(
            "".join(
                [
                    ".",
                    "//span[contains(@class, 'datum')]",
                    "/text()",
                ]
            )
        ).extract()
        starts_on = datetime.strptime(date_without_year.strip(), "%d.%m.")
        starts_on = starts_on.replace(year=datetime.now().year)
        starts_on = pytz.timezone("Europe/Berlin").localize(starts_on)
        starts_on = self.guess_year(starts_on)
        starts_on = str(starts_on.date())
        return starts_on

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

    def parse_thumbnail_url(self, event):
        img_src = event.xpath(
            "".join(
                [
                    ".",
                    "//img",
                    "/@src",
                ]
            )
        ).extract_first()
        # Use wsrv.nl to work around non-https img sources.
        return "https://wsrv.nl/?url=" + urllib.parse.quote(
            "wildatheartberlin.de" + img_src
        )

    def parse_links(self, event):
        links = event.xpath(
            "".join(
                [
                    ".",
                    "//a",
                    "/@href",
                ]
            )
        ).extract()
        links = list(filter(validators.url, links))
        links = links[:10]
        return links
