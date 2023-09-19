import scrapy
import json
from dateparser import parse as parse_date
from lime_chow.items import EventItem
from lime_chow.utils import EventUtils

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
                    "sec-ch-ua": "\"Chromium\";v=\"116\", \"Not)A;Brand\";v=\"24\", \"Brave\";v=\"116\"",
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-model": "\"\"",
                    "sec-ch-ua-platform": "\"Linux\"",
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "sec-gpc": "1",
                    "referer": "https://ra.co/clubs/34420/past-events",
                    "referrer-policy": "strict-origin-when-cross-origin"
                },
                body=json.dumps({
                  "operationName": 'GET_DEFAULT_EVENTS_LISTING',
                  "variables": {
                      "indices": ['EVENT'],
                      "pageSize": 20,
                      "page": 1,
                      "filters": [
                          {
                            "type": 'CLUB',
                            "value": '34420',
                          },
                          {
                            "type": 'DATERANGE',
                            "value": '{"gte":"2023-09-19T15:55:00.000Z"}',
                          },
                      ],
                      "sortOrder": 'ASCENDING',
                      "sortField": 'DATE',
                  },
                  "query": '''
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
                            ...eventFragment
                          }
                        }
                      }
                      
                      fragment eventFragment on IListingItem {
                        ... on Event {
                          id
                          title
                          date
                          contentUrl
                          images {
                            filename
                          }
                          playerLinks {
                            sourceId
                          }
                        }
                      }
                  '''
                }),
                callback=self.parse_response,
            ),
        ]

    def parse_response(self, response):
        response_json = json.loads(response.text)
        events = response_json["data"]["listing"]["data"]
        for event in events:
          venue = self.name
          date = parse_date(event["date"]).strftime("%d/%m/%y")
          title = event["title"]
          url = "https://ra.co" + event["contentUrl"]
          thumbnail_url = event["images"][0]["filename"]
          links = [playerLink["sourceId"] for playerLink in event["playerLinks"]]
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
