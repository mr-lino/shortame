from dataclasses import asdict

import pytest

from shortame.services.url_services import UrlShortener
from shortame.services.key_generation_services import ShortUrlGenerator
from shortame.domain.model import Url
from shortame.adapters.dynamodb_adapter import ShortUrlNotFoundOnTable
from shortame.adapters.redis_adapter import EmptyQueueException


def test_url_shortener_shorten_and_persist(fake_short_url_queue, fake_url_table, fake_cache, sample_url):
    shortener = UrlShortener(queue=fake_short_url_queue, table=fake_url_table, cache=fake_cache)
    
    fake_short_url_queue.enqueue_short_url_key(short_url=sample_url.short_url)

    url = shortener.shorten_and_persist(long_url=sample_url.long_url)

    assert fake_cache.get(short_url=sample_url.short_url) == sample_url.long_url
    assert fake_url_table.get_url(short_url=sample_url.short_url) == asdict(sample_url)
    assert url.short_url == sample_url.short_url
    assert url.long_url == sample_url.long_url

    with pytest.raises(EmptyQueueException) as excinfo:
        shortener.shorten_and_persist(long_url='https://www.example.com')
    
    assert str(excinfo.value) == f"There are no keys left on queue available_urls"

def test_url_shortener_get_long_url(fake_short_url_queue, fake_url_table, fake_cache, sample_url):
    shortener = UrlShortener(queue=fake_short_url_queue, table=fake_url_table, cache=fake_cache)

    fake_cache.add(url=sample_url)

    assert shortener.get_long_url(short_url=sample_url.short_url) == sample_url.long_url

    new_url = Url(short_url='1234xyz', long_url='https://www.example.com')

    fake_url_table.add_url(new_url)

    assert shortener.get_long_url(short_url=new_url.short_url) == new_url.long_url

    with pytest.raises(ShortUrlNotFoundOnTable) as excinfo:
        shortener.get_long_url(short_url='unexistent')
    
    assert str(excinfo.value) == f"Short url 'unexistent' does not exist on url table"


def test_url_shortener_persist_on_table(fake_short_url_queue, fake_url_table, fake_cache, sample_url):
    shortener = UrlShortener(queue=fake_short_url_queue, table=fake_url_table, cache=fake_cache)
    
    shortener._persist_on_table(sample_url)

    assert asdict(sample_url) == fake_url_table.get_url(sample_url.short_url)

def test_url_shortener_fetch_new_short_url(fake_short_url_queue, fake_url_table, fake_cache, sample_url):
    shortener = UrlShortener(queue=fake_short_url_queue, table=fake_url_table, cache=fake_cache)
    
    fake_short_url_queue.enqueue_short_url_key(sample_url.short_url)

    assert shortener._fetch_new_short_url() == sample_url.short_url


def test_url_shortener_add_on_cache(fake_short_url_queue, fake_url_table, fake_cache, sample_url, fake_redis_client):
    shortener = UrlShortener(queue=fake_short_url_queue, table=fake_url_table, cache=fake_cache)

    shortener._add_on_cache(url=sample_url)

    assert fake_redis_client.get(sample_url.short_url).decode('utf-8') == sample_url.long_url
    assert fake_redis_client.ttl(sample_url.short_url) <= shortener.cache.ttl
    assert fake_redis_client.ttl(sample_url.short_url) > -1