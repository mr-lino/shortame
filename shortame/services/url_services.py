from abc import ABC, abstractmethod, abstractclassmethod

from loguru import logger
from loguru._logger import Logger

from shortame.adapters.redis_adapter import AbstractUrlQueue, AbstractCacheQueue, ShortUrlQueue, CacheQueue, EmptyQueueException, ShortUrlNotFound
from shortame.adapters.dynamodb_adapter import AbstractDynamoDBUrlTable, UrlTable
from shortame.domain.model import Url


class AbstractUrlShortener(ABC):
    @abstractmethod
    def shorten_and_persist(self):
        pass

    @abstractmethod
    def fetch_new_short_url(self):
        pass

    @abstractmethod
    def persist_on_table(self):
        pass

    @abstractmethod
    def add_on_cache(self):
        pass

    @abstractmethod
    def get_long_url(self):
        pass


class UrlShortener(AbstractUrlShortener):
    def __init__(
        self,
        queue: AbstractUrlQueue = ShortUrlQueue(),
        table: AbstractDynamoDBUrlTable = UrlTable(),
        cache: AbstractCacheQueue = CacheQueue(),
        logger: Logger = logger,
    ):
        self.queue = queue
        self.table = table
        self.cache = cache
        self.logger = logger

    def shorten_and_persist(self, long_url: str) -> Url:
        try:
            short_url = self.fetch_new_short_url()
            url = Url(short_url=short_url, long_url=long_url)
            self.persist_on_table(url)
        except Exception as e:
            self.logger.error("Error while shortening and persisting url", exc_info=True)
            raise e
        else:
            self.add_on_cache(url)
            return url

    def fetch_new_short_url(self) -> str:
        return self.queue.deque_short_url_key()

    def persist_on_table(self, url: Url):
        return self.table.add_url(url)

    def add_on_cache(self, url: Url):
        return self.cache.add(url)

    def get_long_url(self):
        pass
