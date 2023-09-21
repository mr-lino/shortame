from dataclasses import asdict

from shortame.domain.model import Url
from shortame.adapters.dynamodb_adapter import UrlTable
from shortame.adapters.redis_adapter import ShortUrlQueue
from shortame.services.key_generation_services import ShortUrlGenerator, ShortUrlNotFoundOnTable


def test_short_url_generator_can_enque(fake_short_url_queue, fake_url_table, sample_url):
    fake_short_url_generator = ShortUrlGenerator(queue=fake_short_url_queue, table=fake_url_table)

    assert fake_short_url_generator.generate_and_enque() is True
    
    new_url = Url(short_url=fake_short_url_generator.generate(), long_url="https://example.com")
    fake_url_table.add_url(new_url)

    assert fake_short_url_generator.generate_and_enque(short_url=new_url.short_url) is False


def test_short_url_generator_exists_in_table(fake_short_url_queue, fake_url_table, sample_url):
    fake_short_url_generator = ShortUrlGenerator(queue=fake_short_url_queue, table=fake_url_table)

    assert fake_short_url_generator.exists_in_table(short_url=sample_url.short_url) is True

    new_url = fake_short_url_generator.generate()

    assert fake_short_url_generator.exists_in_table(short_url=new_url) is False

def test_short_url_generator_generate(fake_short_url_queue, fake_table):
    fake_short_url_generator = ShortUrlGenerator(queue=fake_short_url_queue, table=fake_table)

    short_url_1 = fake_short_url_generator.generate()

    assert type(short_url_1) == str
    assert len(short_url_1) == fake_short_url_generator.short_url_size
