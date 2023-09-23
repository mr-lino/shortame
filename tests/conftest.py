from dataclasses import asdict

import boto3
import pytest
from fakeredis import FakeStrictRedis
from moto import mock_dynamodb

from shortame.adapters.dynamodb_adapter import UrlTable
from shortame.adapters.redis_adapter import CacheQueue, ShortUrlQueue
from shortame.domain.model import Url


@pytest.fixture
def sample_url():
    return Url(
        short_url="abcd123", long_url="https://en.wikipedia.org/wiki/Hermeto_Pascoal"
    )


@pytest.fixture
def short_url_queue_name():
    return "available_urls"


@pytest.fixture
def fake_dyn_resource():
    with mock_dynamodb():
        yield boto3.resource(
            "dynamodb",
            aws_access_key_id="fake_id",
            aws_secret_access_key="fake_key",
            aws_session_token="fake_session",
            region_name="sa-east-1",
        )


@pytest.fixture
def fake_table(fake_dyn_resource, sample_url):
    fake_dyn_table = fake_dyn_resource.create_table(
        AttributeDefinitions=[
            {"AttributeName": "short_url", "AttributeType": "S"},
        ],
        TableName="url",
        KeySchema=[{"AttributeName": "short_url", "KeyType": "HASH"}],
        BillingMode="PAY_PER_REQUEST",
    )
    fake_dyn_table.wait_until_exists()
    fake_dyn_table.put_item(Item=asdict(sample_url))


@pytest.fixture
def fake_redis_client():
    return FakeStrictRedis(version=7)


@pytest.fixture
def fake_short_url_queue(fake_redis_client, short_url_queue_name):
    return ShortUrlQueue(
        redis_client=fake_redis_client, queue_name=short_url_queue_name
    )


@pytest.fixture
def fake_url_table(fake_dyn_resource, fake_table):
    return UrlTable(dyn_resource=fake_dyn_resource, table_name="url")


@pytest.fixture
def fake_cache(fake_redis_client):
    return CacheQueue(redis_client=fake_redis_client)
