import logging

import httpx
import pytest

from app.catalog import CatalogClient, UpstreamError


def make(handler):
    return CatalogClient(
        base_url="http://catalog:8000/", timeout=1, transport=httpx.MockTransport(handler)
    )


def test_200_exists_and_path():
    seen = []

    def handler(request):
        seen.append(request.url.path)
        return httpx.Response(200, json={"id": 3})

    assert make(handler).bean_exists(3) is True
    assert seen == ["/api/catalog/beans/3"]


def test_404_not_found():
    assert make(lambda r: httpx.Response(404)).bean_exists(3) is False


@pytest.mark.parametrize("status", [400, 500, 503])
def test_error_status_is_upstream_error(status, caplog):
    with caplog.at_level(logging.WARNING, logger="app.catalog"):
        with pytest.raises(UpstreamError):
            make(lambda r: httpx.Response(status)).bean_exists(3)
    assert f"returned {status}" in caplog.text


@pytest.mark.parametrize("exc", [httpx.ConnectError("boom"), httpx.ReadTimeout("slow")])
def test_connection_error_and_timeout_are_upstream_error(exc, caplog):
    def handler(request):
        raise exc

    with caplog.at_level(logging.WARNING, logger="app.catalog"):
        with pytest.raises(UpstreamError):
            make(handler).bean_exists(3)
    assert "unreachable" in caplog.text
