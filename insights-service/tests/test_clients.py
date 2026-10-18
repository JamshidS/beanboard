from datetime import datetime, timezone

import httpx
import pytest

from app.clients import CatalogClient, NotFoundError, ReviewsClient, UpstreamError

BEAN = {
    "id": 7, "name": "Ethiopia Guji", "roaster": "Onyx", "origin": "Ethiopia",
    "roast": "light", "price_cents": 1850, "flavor_notes": "berry, jasmine",
    "created_at": "2025-01-01T10:00:00Z",
}
REVIEW = {
    "id": "665f1c2e9b1e8a0012345678", "bean_id": 7, "author": "Ana", "rating": 5,
    "comment": "Great", "created_at": "2025-01-02T08:30:00Z",
}
STATS = {"bean_id": 7, "average_rating": 4.5, "review_count": 2}


def make_clients(handler):
    transport = httpx.MockTransport(handler)
    return (
        CatalogClient("http://catalog", transport=transport),
        ReviewsClient("http://reviews", transport=transport),
    )


def recording(body_by_path):
    seen = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append((request.method, request.url.host, request.url.path))
        return httpx.Response(200, json=body_by_path[request.url.path])

    return handler, seen


def test_upstream_paths_and_parsing():
    handler, seen = recording({
        "/api/catalog/beans": [BEAN],
        "/api/catalog/beans/7": BEAN,
        "/api/reviews/beans/7": [REVIEW],
        "/api/reviews/stats": [STATS],
    })
    catalog, reviews = make_clients(handler)

    beans = catalog.list_beans()
    assert beans[0].name == "Ethiopia Guji"
    assert beans[0].created_at == datetime(2025, 1, 1, 10, tzinfo=timezone.utc)
    assert catalog.get_bean(7).price_cents == 1850
    assert reviews.list_reviews(7)[0].rating == 5
    assert reviews.stats()[0].average_rating == 4.5

    assert seen == [
        ("GET", "catalog", "/api/catalog/beans"),
        ("GET", "catalog", "/api/catalog/beans/7"),
        ("GET", "reviews", "/api/reviews/beans/7"),
        ("GET", "reviews", "/api/reviews/stats"),
    ]


def calls(catalog, reviews):
    return [
        catalog.list_beans, lambda: catalog.get_bean(7),
        lambda: reviews.list_reviews(7), reviews.stats,
    ]


def test_404_raises_not_found():
    catalog, reviews = make_clients(lambda r: httpx.Response(404, json={"detail": "nope"}))
    for call in calls(catalog, reviews):
        with pytest.raises(NotFoundError):
            call()


@pytest.mark.parametrize("status", [400, 500, 502, 503])
def test_error_status_raises_upstream_error(status):
    catalog, reviews = make_clients(lambda r: httpx.Response(status))
    for call in calls(catalog, reviews):
        with pytest.raises(UpstreamError):
            call()


@pytest.mark.parametrize("exc", [httpx.ConnectError("refused"), httpx.ReadTimeout("slow")])
def test_transport_failure_raises_upstream_error(exc):
    def handler(request):
        raise exc

    catalog, reviews = make_clients(handler)
    for call in calls(catalog, reviews):
        with pytest.raises(UpstreamError):
            call()


@pytest.mark.parametrize("response", [
    httpx.Response(200, text="<html>oops</html>"),
    httpx.Response(200, text=""),
    httpx.Response(200, json={"unexpected": "object"}),
    httpx.Response(200, json=[{"id": "not-an-int"}]),
    httpx.Response(200, json=None),
])
def test_malformed_200_raises_upstream_error(response):
    catalog, reviews = make_clients(lambda r: response)
    for call in calls(catalog, reviews):
        with pytest.raises(UpstreamError):
            call()
