import boto3
from botocore.exceptions import ClientError
from loguru import logger

from shortame.config import settings

logger.add(sink="create_dynamodb_locally.log")

resource = boto3.resource(
    "dynamodb",
    endpoint_url=settings.dynamodb_endpoint,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region_name,
)
table_name = "url"
logger.info(f"DynamoDB table name: '{table_name}'")
try:
    logger.info(f"Verifying if table '{table_name}' exists")
    resource.Table(table_name).load()
    logger.info(f"Table '{table_name}' was already created")
except ClientError as e:
    if e.response["Error"]["Code"] == "ResourceNotFoundException":
        logger.info(f"Table '{table_name}' does not exists, creating it now")
        table = resource.create_table(
            AttributeDefinitions=[
                {"AttributeName": "short_url", "AttributeType": "S"},
            ],
            TableName=table_name,
            KeySchema=[{"AttributeName": "short_url", "KeyType": "HASH"}],
            BillingMode="PAY_PER_REQUEST",
        )
        table.wait_until_exists()
        logger.info(f"Table {table_name} created")
