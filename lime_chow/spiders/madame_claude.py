import scrapy
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils

class MadameClaudeSpider(scrapy.Spider):
    name = "madame_claude"
    allowed_domains = ["madameclaude.de"]
    start_urls = ['https://madameclaude.de/events/']

    def parse(self, response):
        for event_url in response.xpath("".join([
            "//article",
            "//div[contains(@class, 'title')]",
            "//a",
            "/@href",
        ])).extract():
            yield scrapy.Request(url=event_url, callback=self.parse_event)

    def parse_event(self, response):
        venue = self.name
        date = response.xpath("".join([
            "//article",
            "//div[contains(@class, 'date')]",
            "//p[contains(@class, 'numbers')]",
            "//text()",
        ])).extract_first()
        title = response.xpath("".join([
            "//article",
            "//h2",
            "/text()",
        ])).extract_first()
        url = response.url
        thumbnail_url = response.xpath("".join([
            "//article",
            "//img",
            "/@src",
        ])).extract_first()
        links = response.xpath("".join([
            "//article",
            "//div[contains(@class, 'info')]",
            "//a",
            "/@href",
        ])).extract()[:10]
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
