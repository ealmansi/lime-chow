import scrapy
from urllib.parse import urljoin
import validators
from urlextract import URLExtract
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils

class ArkaodaSpider(scrapy.Spider):
    name = "arkaoda"
    allowed_domains = ["berlin.arkaoda.com"]
    start_urls = ["https://berlin.arkaoda.com/?/default/program"]

    def parse(self, response):
        hrefs = response.xpath("//a/@href").extract()
        event_urls = set([
            urljoin(response.url, href)
            for href in hrefs
            if "/default/detail" in href
        ])
        for event_url in event_urls:
            yield scrapy.Request(url=event_url, callback=self.parse_event)

    def parse_event(self, response):
        venue = self.name
        date = self.get_event_date(response)
        title = response.css(
            "article h6::text"
        ).extract_first().strip()
        url = response.url
        thumbnail_url = urljoin(
            "https://berlin.arkaoda.com",
            response.css(
                "aside img::attr(src)"
            ).extract_first().strip()
        )
        links = self.get_event_links(response)
        yield EventItem(
            id = EventUtils.build_id(venue, date, title),
            extracted_at = EventUtils.get_current_datetime(),
            venue = venue,
            date = date,
            title = title,
            url = url,
            thumbnail_url = thumbnail_url,
            links = links,
        )

    def get_event_date(self, response):
        date = response.css(".excerpt div b::text").extract_first()
        [day, month, year] = date.split(" / ")
        return "/".join([day, month, year[2:]])

    def get_event_links(self, response):
        texts = response.css(
            ".excerpt p ::text"
        ).extract()
        url_extract = URLExtract()
        links = [
            url
            for urls in list(map(url_extract.find_urls, texts))
            for url in urls
        ]
        links = list(filter(validators.url, links))
        links = links[:10]
        return links
