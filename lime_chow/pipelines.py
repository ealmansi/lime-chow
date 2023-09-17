import boto3

class LimeChowPipeline:
    def open_spider(self, _):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = 'events'
        self.table = self.dynamodb.Table('events')
        self.table.load()

    def process_item(self, item, _):
        self.table.put_item(
            TableName=self.table_name,
            Item=dict(item),
        )
        return item

    def close_spider(self, _):
        self.table = None
        self.dynamodb = None
