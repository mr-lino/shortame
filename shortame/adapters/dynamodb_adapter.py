# File with adapter for dynamodb usage
from dataclasses import asdict
from abc import ABC, abstractmethod

from loguru import logger
from botocore.exceptions import ClientError
from mypy_boto3_dynamodb.service_resource import Table, DynamoDBServiceResource

from shortame.domain.model import Url


class AbstractDynamoDBTable(ABC):
    @abstractmethod
    def _load_table(self):
        pass

    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def get(self):
        pass


class FakeDynamoDBTable(AbstractDynamoDBTable):
    def __init__(self, table_name: str):
        self.table_name = table_name
        self._contents = {}
    
    def _load_table(self):
        return True
    
    def add(self, url: Url):
        self._contents.update({url.short_url: asdict(url)})

    def get(self, short_url: str) -> dict[str, str, str, str] | None:
        return self._contents.get(short_url)


class UrlTable(AbstractDynamoDBTable):
    """Encapsulates an Amazon DynamoDB table of shortened urls."""

    def __init__(self, dyn_resource: DynamoDBServiceResource, table_name: str = "url"):
        """
        Initializes a UrlTable object.

        :param dyn_resource: A Boto3 DynamoDB resource.
        :param table_name: the name of the DynamoDB table, default to 'url'.
        """
        self.dyn_resource = dyn_resource
        self.table_name = table_name
        self.table = self._load_table(table_name)

    def _load_table(self, table_name: str) -> Table:
        """Tries to load a table using the table's name."""
        try:
            logger.info(f"Attempting to load table '{self.table_name}'")
            table = self.dyn_resource.Table(self.table_name)
            table.load()
        except ClientError as err:
            if err.response["Error"]["Code"] == "ResourceNotFoundException":
                return None
            else:
                error_response = err.response["Error"]["Code"]
                error_message = err.response["Error"]["Message"]
                logger.error(
                    f"Couldn't check for existence of {table_name}. Here's why: {error_response}: {error_message}",
                )
                raise
        else:
            return table

    def add(self, url: Url) -> None:
        """Add Url object to the database."""
        try:
            logger.info(f"Adding url {url.short_url} to database")
            self.table.put_item(Item=asdict(url))
        except ClientError as err:
            error_code = err.response["Error"]["Code"]
            error_message = err.response["Error"]["Message"]
            logger.error(
                f"Couldn't add url {url.short_url} to table {self.table_name}. Here's why: {error_code}: {error_message}"
            )
            raise

    def get(self, short_url: str) -> dict[str, str, str, str] | None:
        """
        Gets a url from the database given a short_url input.

        :param short_url: the path of the shortened url, e.g.: xyz1234
        :return:
        """
        try:
            response = self.table.get_item(Key={"short_url": short_url})
        except ClientError as err:
            error_code = err.response["Error"]["Code"]
            error_message = err.response["Error"]["Message"]
            logger.error(
                "Couldn't get short_url '{short_url}' from url table. Here's why: {error_code}: {error_message}"
            )
            raise
        else:
            return response.get("Item")
