from abc import ABC, abstractmethod

from fakeredis import FakeStrictRedis
from loguru import logger
from loguru._logger import Logger
from redis import Redis

from shortame.config import get_redis_host_and_port

r = Redis(**get_redis_host_and_port())


class EmptyQueueException(Exception):
    pass


class AbstractRedisQueue(ABC):
    @abstractmethod
    def deque_short_url_key():
        pass

    @abstractmethod
    def enqueue_short_url_key():
        pass


class FakeShortUrlQueue(AbstractRedisQueue):
    """Fake implementation of a ShortURLQueue for testing purposes."""

    def __init__(
        self,
        redis_client: FakeStrictRedis = FakeStrictRedis(version=7),
        queue_name: str = "available_urls",
        logger: Logger = logger,
    ):
        self.redis_client = redis_client
        self.queue_name = queue_name
        self.logger = logger

    def deque_short_url_key(self):
        key = self.redis_client.rpop(self.queue_name)
        return key.decode("utf-8")

    def enqueue_short_url_key(self, short_url: str) -> int:
        return self.redis_client.lpush(self.queue_name, short_url)


class ShortUrlQueue(AbstractRedisQueue):
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
            queue_size = self.redis_client.lpush(self.queue_name, short_url)
        except Exception as e:
            self.logger.error(
                f"Error while enqueing short url on queue {self.queue_name}"
            )
            raise e
        else:
            return queue_size
