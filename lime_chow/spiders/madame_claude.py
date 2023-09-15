import scrapy
import re
from datetime import datetime
from lime_chow.items import LimeChowItem

class MadameClaudeSpider(scrapy.Spider):
    name = "madame_claude"
    allowed_domains = ["madameclaude.de"]
    start_urls = ['https://madameclaude.de/events/']

    def parse(self, response):
        for event_url in response.xpath(
            "//article//div[contains(@class, 'title')]//a/@href"
        ).extract():
            yield scrapy.Request(url=event_url, callback=self.parse_event)

    def parse_event(self, response):
        title = response.xpath(
            "//article//h2/text()"
        ).extract_first()
        date = response.xpath(
            "//article//div[contains(@class, 'date')]//p[contains(@class, 'numbers')]//text()"
        ).extract_first()
        yield LimeChowItem(
            id = (
                "madame-claude-" + re.sub("[^a-z0-9]+", "-", date + "-" + title.lower()).strip("-")
            )[:80],
            url = response.url,
            title = title,
            date = date,
            thumbnail_url = response.xpath(
                "//article//img/@src"
            ).extract_first(),
            extracted_at = datetime.now().isoformat()
        )
