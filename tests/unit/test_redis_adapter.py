import pytest

from shortame.adapters.redis_adapter import (CacheQueue, EmptyQueueException,
                                             ShortUrlQueue)


def test_short_url_queue_can_deque(fake_redis_client, short_url_queue_name, sample_url):
    short_url = sample_url.short_url
    fake_redis_client.lpush(short_url_queue_name, short_url)

    queue = ShortUrlQueue(
        redis_client=fake_redis_client, queue_name=short_url_queue_name
    )

    assert short_url == queue.deque_short_url_key()

    with pytest.raises(EmptyQueueException) as excinfo:
        queue.deque_short_url_key()

    assert (
        str(excinfo.value) == f"There are no keys left on queue {short_url_queue_name}"
    )


def test_short_url_queue_can_enque(fake_redis_client, sample_url, short_url_queue_name):
    queue = ShortUrlQueue(
        redis_client=fake_redis_client, queue_name=short_url_queue_name
    )

    queue_size = queue.enqueue_short_url_key(sample_url.short_url)

    assert queue_size == fake_redis_client.llen(short_url_queue_name)
    assert sample_url.short_url == fake_redis_client.rpop(short_url_queue_name).decode(
        "utf-8"
    )


def test_short_url_queue_size(fake_redis_client, short_url_queue_name):
    queue = ShortUrlQueue(
        redis_client=fake_redis_client, queue_name=short_url_queue_name
    )

    for i in range(5):
        fake_redis_client.lpush(short_url_queue_name, i)

    assert queue.current_size() == 5


def test_cache_queue_can_add():
    pass


def test_cache_queue_can_get():
    pass
