from abc import ABC, abstractmethod

from loguru import logger
from loguru._logger import Logger

from shortame.adapters.dynamodb_adapter import (AbstractDynamoDBUrlTable,
                                                UrlTable)
from shortame.adapters.redis_adapter import (AbstractCacheQueue,
                                             AbstractUrlQueue, CacheQueue,
                                             ShortUrlNotFoundOnCache,
                                             ShortUrlQueue)
from shortame.domain.model import Url


class AbstractUrlShortener(ABC):
    @abstractmethod
    def shorten_and_persist(self):
        pass

    @abstractmethod
    def _fetch_new_short_url(self):
        pass

    @abstractmethod
    def _persist_on_table(self):
        pass

    @abstractmethod
    def _add_on_cache(self):
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
            short_url = self._fetch_new_short_url()
            url = Url(short_url=short_url, long_url=long_url)
            self._persist_on_table(url)
        except Exception as e:
            self.logger.error(
                "Error while shortening and persisting url", exc_info=True
            )
            raise e
        else:
            self._add_on_cache(url)
            return url

    def _fetch_new_short_url(self) -> str:
        return self.queue.deque_short_url_key()

    def _persist_on_table(self, url: Url):
        return self.table.add_url(url)

    def _add_on_cache(self, url: Url):
        return self.cache.add(url)

    def get_long_url(self, short_url: str):
        try:
            long_url = self.cache.get(short_url)
        except ShortUrlNotFoundOnCache:
            try:
                url = self.table.get_url(short_url)
                return url["long_url"]
            except Exception as e:
                self.logger.error(
                    f"Error while retrieving correspoding long url from '{short_url}' from table"
                )
                raise e
            pass
        except Exception as e:
            self.logger.error(
                f"Error while retrieving corresponding long url from '{short_url}' from cache",
                exc_info=True,
            )
            raise e
        else:
            return long_url
