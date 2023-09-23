import pytest
from pydantic import ValidationError

from shortame.domain.model import Url


def test_url_creational_params():
    short_url = "ABC123a"
    long_url = "https://example.com"

    url = Url(short_url=short_url, long_url=long_url)

    assert url.short_url == short_url
    assert url.long_url == long_url

    with pytest.raises(ValidationError) as excinfo:
        Url(short_url=1234, long_url="https://example.com")

    assert "Input should be a valid string" in str(excinfo.value)

    with pytest.raises(ValidationError) as excinfo:
        Url(short_url=short_url)

    assert "Field required [type=missing" in str(excinfo.value)
