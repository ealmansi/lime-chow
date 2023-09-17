import boto3

def create_events_table(dynamodb):
    table_name = 'events'
    table = dynamodb.create_table(
        TableName=table_name,
        BillingMode='PAY_PER_REQUEST',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH',
            },
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S',
            },
        ],
    )
    table.wait_until_exists()

if __name__ == '__main__':
    dynamodb = boto3.resource('dynamodb')
    create_events_table(dynamodb)
