# File with adapter for dynamodb usage
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Dict

import boto3
from botocore.exceptions import ClientError
from loguru import logger
from loguru._logger import Logger
# from moto import mock_dynamodb
from mypy_boto3_dynamodb.service_resource import DynamoDBServiceResource, Table

from shortame.config import settings
from shortame.domain.model import Url

dyn_resource = boto3.resource(
    "dynamodb",
    endpoint_url=settings.dynamodb_endpoint,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region_name,
)


# @mock_dynamodb
# def get_fake_dyn_resource():
#     return boto3.resource(
#         "dynamodb",
#         aws_access_key_id="fake_id",
#         aws_secret_access_key="fake_key",
#         aws_session_token="fake_session",
#         region_name="sa-east1",
#     )
class ShortUrlNotFoundOnTable(Exception):
    pass


class AbstractDynamoDBUrlTable(ABC):
    """Abstract Dynamo DB table"""

    @abstractmethod
    def _load_table(self):
        pass

    @abstractmethod
    def add_url(self):
        pass

    @abstractmethod
    def get_url(self):
        pass


# class FakeUrlTable(AbstractDynamoDBUrlTable):
#     def __init__(
#         self,
#         dyn_resource: DynamoDBServiceResource = get_fake_dyn_resource(),
#         table_name: str = "url",
#         logger: Logger = logger,
#     ):
#         self.dyn_resource = dyn_resource
#         self.table_name = table_name
#         self.logger = logger
#         self.table = self._load_table(self.table_name)

#     def _load_table(self, table_name: str):
#         return self.dyn_resource.Table(table_name)

#     def add_url(self, url: Url):
#         self.table.put_item(Item=asdict(url))

#     def get_url(self, short_url: str) -> dict[str, str, str, str] | None:
#         response = self.table.get_item(Key={"short_url": short_url})
#         return response.get("Item")


class UrlTable(AbstractDynamoDBUrlTable):
    """Encapsulates an Amazon DynamoDB table of shortened urls."""

    def __init__(
        self,
        dyn_resource: DynamoDBServiceResource = dyn_resource,
        table_name: str = "url",
        logger: Logger = logger,
    ):
        """
        Initializes a UrlTable object.

        :param dyn_resource: A Boto3 DynamoDB resource.
        :param table_name: the name of the DynamoDB table, default to 'url'.
        """
        self.dyn_resource = dyn_resource
        self.table_name = table_name
        self.logger = logger
        self.table = self._load_table(table_name)

    def _load_table(self, table_name: str) -> Table:
        """Tries to load a table using the table's name."""
        try:
            self.logger.info(f"Attempting to load table '{self.table_name}'")
            table = self.dyn_resource.Table(self.table_name)
            table.load()
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                return None
            else:
                error_response = err.response["Error"]["Code"]
                error_message = err.response["Error"]["Message"]
                self.logger.error(
                    f"Couldn't check for existence of {table_name}. Here's why: {error_response}: {error_message}",
                )
                raise
        else:
            return table

    def add_url(self, url: Url) -> None:
        """Add Url object to the database."""
        try:
            self.logger.info(f"Adding url {url.short_url} to database")
            self.table.put_item(Item=asdict(url))
            self.logger.info(f"Successfully added url '{url}' on table")
        except ClientError as err:
            error_code = err.response["Error"]["Code"]
            error_message = err.response["Error"]["Message"]
            self.logger.error(
                f"Couldn't add url {url.short_url} to table {self.table_name}."
            )
            self.logger.error(f"Here's why: {error_code}: {error_message}")
            raise

    def get_url(self, short_url: str) -> Dict[str, str] | None:
        """
        Gets a original long url from the database given a short_url input.

        :param short_url: the path of the shortened url, e.g.: xyz1234
        :return url: the url dict with the long and short versions
        """
        try:
            self.logger.info(
                f"Attempting to get '{short_url}' from  {self.table_name} table"
            )
            response = self.table.get_item(Key={"short_url": short_url})
        except ClientError as err:
            error_code = err.response["Error"]["Code"]
            error_message = err.response["Error"]["Message"]
            self.logger.error(
                f"Couldn't get short url '{short_url}' from {self.table_name} table."
            )
            self.logger.error(f"Here's why: {error_code}: {error_message}")
            raise
        else:
            if not response.get("Item"):
                raise ShortUrlNotFoundOnTable(
                    f"Short url '{short_url}' does not exist on {self.table_name} table"
                )
            self.logger.info(f"Successfully fetched url '{url.__str__}' from table")
            return response.get("Item")
