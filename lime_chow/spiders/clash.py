import scrapy
import validators
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils

class ClashSpider(scrapy.Spider):
    name = "clash"
    allowed_domains = ["clash-berlin.de"]
    start_urls = ["https://clash-berlin.de/"]

    def parse(self, response):
        for event in response.css(".gigs-container .item"):
            venue = self.name
            date = self.get_event_date(event)
            title = event.css(".gig-title::text").extract_first().strip()
            url = response.url
            thumbnail_url = event.css(".flyer img::attr(src)").extract_first()
            links = self.get_event_links(event)
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

    def get_event_date(self, event):
        date = event.css(".dateTwo::text").extract_first()
        return date.replace(".", "/")

    def get_event_links(self, event):
        links = event.css(".info-extra a::attr(href)").extract()
        links = list(filter(validators.url, links))
        links = links[:10]
        return links
