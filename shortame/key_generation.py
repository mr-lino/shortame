from abc import ABC, abstractmethod, abstractstaticmethod
from secrets import choice
from string import ascii_letters, digits

from loguru import logger
from loguru._logger import Logger

from shortame.adapters.redis_adapter import AbstractUrlQueue, ShortUrlQueue
from shortame.adapters.dynamodb_adapter import AbstractDynamoDBUrlTable, UrlTable, ShortURLNotFound

class AbstractShortUrlGenerator(ABC):
    """Abstract Short Url Generator"""
    def __init__(self, queue: AbstractUrlQueue, table: AbstractDynamoDBUrlTable):
        self.queue = queue
        self.table = table

    @abstractstaticmethod
    def generate_and_enque():
        pass

    @abstractmethod
    def exists_in_table(self):
        pass

    @abstractstaticmethod
    def generate():
        pass


class ShortUrlGenerator(AbstractShortUrlGenerator):
    """Encapsulates the logic for creating and enqueing short urls"""
    def __init__(self, logger: Logger = logger):
        super().__init__(queue = ShortUrlQueue(), table = UrlTable())
        self.logger = logger
    
    def generate_and_enque(self, size: int = 7) -> None:
        """
        Generate a new short url and enqueue it if it's not already present in the database.
        
        :param size: the size of the short url to be generated
        """
        self.logger.info(f"Generating a new short url with size {size}")
        short_url = self.generate(size=size)
        if not self.exists_in_table(short_url=short_url):
            self.queue.enqueue_short_url_key(short_url=short_url)

    def exists_in_table(self, short_url: str) -> bool:
        """
        Verifies is a given short url is not present in the database

        :param short_url: the short url to be verified, e.g.: xyz1234
        :return exists: states if the short url is present or not
        """
        self.logger.info(f"Verifying the existence of key {short_url} on table {self.table.table_name}")
        try:
            self.table.get_url(short_url=short_url)
        except ShortURLNotFound as s:
            self.logger.info(f"Short url '{short_url}' is good to go")
            return False
        except Exception as e:
            pass
        else:
            self.logger.info(f"Short url '{short_url}' is already taken")
            return True
    
    @staticmethod
    def generate(size: int = 7) -> str:
        """
        Generate a new short url, given a input size.

        :param size: the size of the new url, e.g.: 7
        :return short_url: the new url, e.g.: xyz1234

        """
        short_url = ''.join((choice(ascii_letters + digits) for i in range(size)))
        return short_url