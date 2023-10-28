import time
from datetime import datetime
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils
import json
import pytz
import scrapy


class SameheadsSpider(scrapy.Spider):
    name = "sameheads"

    def start_requests(self):
        return [
            scrapy.Request(
                url="https://ra.co/graphql",
                method="POST",
                headers={
                    "accept": "*/*",
                    "accept-language": "en-US,en;q=0.9",
                    "content-type": "application/json",
                    "ra-content-language": "en",
                    "sec-ch-ua": '"Chromium";v="116", "Not)A;Brand";v="24", "Brave";v="116"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-model": '""',
                    "sec-ch-ua-platform": '"Linux"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "sec-gpc": "1",
                    "referer": "https://ra.co/clubs/34420/past-events",
                    "referrer-policy": "strict-origin-when-cross-origin",
                },
                body=json.dumps(
                    {
                        "operationName": "GET_DEFAULT_EVENTS_LISTING",
                        "variables": {
                            "indices": ["EVENT"],
                            "pageSize": 20,
                            "page": 1,
                            "filters": [
                                {
                                    "type": "CLUB",
                                    "value": "34420",
                                },
                                {
                                    "type": "DATERANGE",
                                    "value": '{"gte":"'
                                    + datetime.now().isoformat()
                                    + '"}',
                                },
                            ],
                            "sortOrder": "ASCENDING",
                            "sortField": "DATE",
                        },
                        "query": """
                      query GET_DEFAULT_EVENTS_LISTING(
                        $indices: [IndexType!],
                        $filters: [FilterInput],
                        $pageSize: Int,
                        $page: Int,
                        $sortField: FilterSortFieldType,
                        $sortOrder: FilterSortOrderType,
                      ) {
                        listing(
                          indices: $indices,
                          aggregations: [],
                          filters: $filters,
                          pageSize: $pageSize,
                          page: $page,
                          sortField: $sortField,
                          sortOrder: $sortOrder
                        ) {
                          data {
                            ... on Event {
                              id
                              title
                              date
                              startTime
                              contentUrl
                              images {
                                filename
                              }
                              playerLinks {
                                sourceId
                              }
                            }
                          }
                        }
                      }
                  """,
                    }
                ),
                callback=self.parse_response,
            ),
        ]

    def parse_response(self, response):
        response_json = json.loads(response.text)
        events = response_json["data"]["listing"]["data"]
        for event in events:
            venue = self.name
            starts_at = datetime.fromisoformat(event["startTime"])
            starts_at = pytz.timezone("Europe/Berlin").localize(starts_at)
            starts_on = str(starts_at.date())
            starts_at = starts_at.isoformat()
            title = event["title"]
            assert title is not None
            content_url = event["contentUrl"]
            assert content_url is not None
            url = "https://ra.co" + content_url
            images = event["images"]
            assert images is not None and len(images) > 0
            thumbnail_url = event["images"][0]["filename"]
            assert thumbnail_url is not None
            player_links = event["playerLinks"]
            assert player_links is not None
            links = []
            for player_link in player_links:
                source_id = player_link["sourceId"]
                assert source_id is not None
                links.append(source_id)
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
