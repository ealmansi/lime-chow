import time
from datetime import datetime
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils
import pytz
import scrapy
import validators


class SchokoladenSpider(scrapy.Spider):
    name = "schokoladen"
    allowed_domains = ["schokoladen-mitte.de"]
    start_urls = ["https://schokoladen-mitte.de/"]

    def parse(self, response):
        for event in response.css(".event"):
            venue = self.name
            starts_on, starts_at = self.parse_starts_on(event)
            title = (
                event.xpath(
                    "".join(
                        [
                            ".",
                            "//div[contains(@class, 'title')]",
                            "//div",
                            "/text()",
                        ]
                    )
                )
                .extract_first()
                .strip()
            )
            url = (
                event.xpath(
                    "".join(
                        [
                            ".",
                            "//a[contains(@class, 'ticketlink')]",
                            "/@href",
                        ]
                    )
                ).extract_first()
                or response.url
            )
            thumbnail_url = "https://www.schokoladen-mitte.de" + (
                event.xpath(
                    "".join(
                        [
                            ".",
                            "//div[contains(@class, 'imageWrapper')]",
                            "//img",
                            "/@src",
                        ]
                    )
                ).extract_first()
                or event.xpath(
                    "".join(
                        [
                            ".",
                            "//div[contains(@class, 'carousel-item')]",
                            "//img",
                            "/@src",
                        ]
                    )
                ).extract_first()
            )
            links = self.parse_event_links(event)
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
                ttl=int(time.time() + 36 * 3600),
            )

    def parse_starts_on(self, event):
        [_, date_without_year, uhr, *_] = event.xpath(
            "".join(
                [
                    ".",
                    "//div[contains(@class, 'eventHeader')]",
                    "//div[contains(@class, 'subHeader')]",
                    "//span",
                    "/text()",
                ]
            )
        ).extract()
        time = uhr[: -len(" Uhr")]
        starts_at = date_without_year.strip() + " " + time.strip()
        starts_at = datetime.strptime(starts_at, "%d.%m. %H:%M")
        starts_at = starts_at.replace(year=datetime.now().year)
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

    def parse_event_links(self, event):
        # TODO: Retrieve more links from description, which is
        # loaded dynamically upon pressing the button "open".
        links = event.xpath(
            "".join(
                [
                    ".",
                    "//div[contains(@class, 'links')]",
                    "//a",
                    "/@href",
                ]
            )
        ).extract()
        links = list(filter(validators.url, links))
        links = links[:10]
        return links
