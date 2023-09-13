import boto3

from shortame.config import settings

client = boto3.resource(
    "dynamodb",
    endpoint_url=settings.dynamodb_endpoint,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region_name,
)
table_name = "url"
table = client.create_table(
    AttributeDefinitions=[
        {"AttributeName": "short_url", "AttributeType": "S"},
    ],
    TableName=table_name,
    KeySchema=[{"AttributeName": "short_url", "KeyType": "HASH"}],
    BillingMode="PAY_PER_REQUEST",
)
table.wait_until_exists()
