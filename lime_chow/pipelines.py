from scrapy.exceptions import NotConfigured
import boto3


class DynamoDbPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def __init__(self, crawler):
        if not crawler.settings.getbool("DYNAMO_DB_PIPELINE_ENABLED"):
            raise NotConfigured

    def open_spider(self, _):
        self.dynamo_db = boto3.resource("dynamodb")
        self.events_table_name = "events"
        self.events_table = self.dynamo_db.Table(self.events_table_name)
        self.events_table.load()

    def process_item(self, item, _):
        self.events_table.put_item(
            TableName=self.events_table_name,
            Item=dict(item),
        )
        return item

    def close_spider(self, _):
        self.events_table = None
        self.dynamo_db = None
