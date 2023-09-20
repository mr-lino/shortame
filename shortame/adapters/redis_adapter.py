from abc import ABC, abstractmethod

from fakeredis import FakeStrictRedis
from loguru import logger
from loguru._logger import Logger
from redis import Redis

from shortame.config import get_redis_host_and_port
from shortame.domain.model import Url

r = Redis(**get_redis_host_and_port())


class EmptyQueueException(Exception):
    pass


class ShortUrlNotFoundOnCache(Exception):
    pass


class AbstractUrlQueue(ABC):
    @abstractmethod
    def deque_short_url_key(self):
        pass

    @abstractmethod
    def enqueue_short_url_key(self):
        pass

    @abstractmethod
    def current_size(self):
        pass


class AbstractCacheQueue(ABC):
    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def get(self):
        pass

class ShortUrlQueue(AbstractUrlQueue):
    """Encapsulates the Redis queue containing available short urls"""

    def __init__(
        self,
        redis_client: Redis = r,
        queue_name: str = "available_urls",
        logger: Logger = logger,
    ):
        self.redis_client = redis_client
        self.queue_name = queue_name
        self.logger = logger

    def deque_short_url_key(self) -> str:
        try:
            self.logger.info(
                f"Dequeing an available short url from queue {self.queue_name}"
            )
            key = self.redis_client.rpop(self.queue_name)
        except Exception as e:
            self.logger.error(
                f"Error while dequeing short url from queue {self.queue_name}"
            )
            raise e
        else:
            if not key:
                raise EmptyQueueException(
                    f"There are no keys left on queue {self.queue_name}"
                )
            return key.decode("utf-8")

    def enqueue_short_url_key(self, short_url: str) -> int:
        try:
            self.logger.info(f"Enqueing short url on queue {self.queue_name}")
            queue_size = self.redis_client.lpush(self.queue_name, short_url)
        except Exception as e:
            self.logger.error(
                f"Error while enqueing short url on queue {self.queue_name}"
            )
            raise e
        else:
            return queue_size

    def current_size(self) -> int:
        try:
            self.logger.info(f"Fetching the current size of queue {self.queue_name}")
            queue_size = self.redis_client.llen(self.queue_name)
        except Exception as e:
            self.logger.error(
                f"Error while fetching the current size of queue {self.queue_name}"
            )
            raise e
        else:
            return queue_size


class CacheQueue(AbstractCacheQueue):
    def __init__(self, redis_client: Redis = r, logger: Logger = logger):
        self.redis_client = redis_client
        self.logger = logger
        self.ttl = 30 * 24 * 60 * 60

    def add(self, url: Url) -> bool:
        try:
            self.logger.info(f"Adding url '{url}' to the cache")
            added = self.redis_client.set(url.short_url, url.long_url, ex=self.ttl)
        except Exception as e:
            self.logger.error(f"Error while adding {url} to the cache")
            raise e
        return added

    def get(self, short_url: str) -> str:
        try:
            self.logger.info(f"Retrieving short url '{short_url}' from cache")
            long_url = self.redis_client.get(short_url)
        except Exception as e:
            self.logger.error(f"Error while getting '{short_url}' from cache")
            raise e
        else:
            if not long_url:
                raise ShortUrlNotFoundOnCache(
                    f"Short url '{short_url}' not found on cache"
                )
            self.logger.info(
                f"Long url for the given key is '{long_url.decode('utf-8')[:30]}...'"
            )
            return long_url.decode("utf-8")
