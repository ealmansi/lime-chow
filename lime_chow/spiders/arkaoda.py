from datetime import datetime
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils
from urlextract import URLExtract
from urllib.parse import urljoin
import pytz
import scrapy
import validators


class ArkaodaSpider(scrapy.Spider):
    name = "arkaoda"
    allowed_domains = ["berlin.arkaoda.com"]
    start_urls = ["https://berlin.arkaoda.com/?/default/program"]

    def parse(self, response):
        hrefs = response.xpath("//a/@href").extract()
        event_urls = set(
            [urljoin(response.url, href) for href in hrefs if "/default/detail" in href]
        )
        for event_url in event_urls:
            yield scrapy.Request(url=event_url, callback=self.parse_event)

    def parse_event(self, response):
        venue = self.name
        starts_on = self.parse_starts_on(response)
        title = response.css("article h6::text").extract_first().strip()
        url = response.url
        thumbnail_url = urljoin(
            "https://berlin.arkaoda.com",
            response.css("aside img::attr(src)").extract_first().strip(),
        )
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

    def parse_starts_on(self, response):
        date = response.css(".excerpt div b::text").extract_first()
        assert date is not None
        starts_on = datetime.strptime(date.strip(), "%d / %m / %Y")
        starts_on = pytz.timezone("Europe/Berlin").localize(starts_on)
        starts_on = str(starts_on.date())
        return starts_on

    def parse_links(self, response):
        texts = response.css(".excerpt p ::text").extract()
        url_extract = URLExtract()
        links = [
            url for urls in list(map(url_extract.find_urls, texts)) for url in urls
        ]
        links = list(filter(validators.url, links))
        links = links[:10]
        return links
