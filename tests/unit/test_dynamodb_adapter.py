from dataclasses import asdict

import pytest

from shortame.adapters.dynamodb_adapter import (ShortUrlNotFoundOnTable,
                                                UrlTable)
from shortame.domain.model import Url
from tests.conftest import sample_url


def test_url_table_loads_the_correct_table(fake_dyn_resource, fake_table):
    ok_table_name = "url"
    not_ok_table_name = "wrong_table"
    ok_url_table = UrlTable(dyn_resource=fake_dyn_resource, table_name=ok_table_name)
    not_ok_url_table = UrlTable(
        dyn_resource=fake_dyn_resource, table_name=not_ok_table_name
    )

    assert ok_url_table.table_name == fake_dyn_resource.Table("url").table_name
    assert not_ok_url_table.table_name != fake_dyn_resource.Table("url").table_name


def test_url_table_can_add_url(fake_dyn_resource, fake_table):
    short_url = "xyz1234"
    long_url = "https://www.google.com"
    table_name = "url"

    url_table = UrlTable(dyn_resource=fake_dyn_resource, table_name=table_name)
    url = Url(short_url=short_url, long_url=long_url)

    assert url_table.add_url(url) is True

    not_ok_url_table = UrlTable(
        dyn_resource=fake_dyn_resource, table_name="wrong_table"
    )

    with pytest.raises(AttributeError) as excinfo:
        not_ok_url_table.add_url(url)

    assert str(excinfo.value) == "'NoneType' object has no attribute 'put_item'"


def test_url_table_can_get_url(fake_dyn_resource, fake_table):
    table_name = "url"
    short_url = sample_url.short_url

    url_table = UrlTable(dyn_resource=fake_dyn_resource, table_name=table_name)
    from_db = url_table.get_url(short_url=short_url)

    assert from_db == asdict(sample_url)
    assert from_db["short_url"] == sample_url.short_url
    assert from_db["long_url"] == sample_url.long_url

    not_ok_short_url = "notexists"

    with pytest.raises(ShortUrlNotFoundOnTable) as excinfo:
        url_table.get_url(short_url=not_ok_short_url)

    assert (
        str(excinfo.value)
        == f"Short url '{not_ok_short_url}' does not exist on {table_name} table"
    )
