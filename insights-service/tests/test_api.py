from datetime import datetime, timezone

import httpx
import pytest
from fastapi.testclient import TestClient

from app.clients import (
    CatalogClient,
    NotFoundError,
    ReviewsClient,
    UpstreamError,
    get_catalog_client,
    get_reviews_client,
)
from app.main import app
from app.schemas import Bean, BeanStats, Review

NOW = datetime(2025, 1, 1, tzinfo=timezone.utc)


def make_bean(bean_id: int, name: str) -> Bean:
    return Bean(
        id=bean_id, name=name, roaster="R", origin="O", roast="light",
        price_cents=1000, flavor_notes="x", created_at=NOW,
    )


def make_review(index: int, bean_id: int, rating: int) -> Review:
    return Review(
        id=str(index), bean_id=bean_id, author="Ana", rating=rating,
        comment="", created_at=NOW,
    )


class FakeCatalog:
    def __init__(self, beans=None, fail=False, missing=False):
        self.beans = beans or []
        self.fail = fail
        self.missing = missing

    def list_beans(self):
        if self.missing:
            raise NotFoundError("/api/catalog/beans")
        if self.fail:
            raise UpstreamError("catalog down")
        return self.beans

    def get_bean(self, bean_id):
        if self.fail:
            raise UpstreamError("catalog down")
        for bean in self.beans:
            if bean.id == bean_id:
                return bean
        raise NotFoundError(str(bean_id))


class FakeReviews:
    def __init__(self, reviews=None, stats=None, fail=False, missing=False):
        self.reviews = reviews or []
        self._stats = stats or []
        self.fail = fail
        self.missing = missing

    def list_reviews(self, bean_id):
        if self.fail:
            raise UpstreamError("reviews down")
        return [r for r in self.reviews if r.bean_id == bean_id]

    def stats(self):
        if self.missing:
            raise NotFoundError("/api/reviews/stats")
        if self.fail:
            raise UpstreamError("reviews down")
        return self._stats


@pytest.fixture
def use_fakes():
    def _use(catalog, reviews):
        app.dependency_overrides[get_catalog_client] = lambda: catalog
        app.dependency_overrides[get_reviews_client] = lambda: reviews
        return TestClient(app)

    yield _use
    app.dependency_overrides.clear()


def test_health(use_fakes):
    assert use_fakes(FakeCatalog(), FakeReviews()).get("/health").json() == {"status": "ok"}


def test_leaderboard_sorts_and_puts_unrated_last(use_fakes):
    beans = [make_bean(1, "A"), make_bean(2, "B"), make_bean(3, "C"), make_bean(4, "D")]
    stats = [
        BeanStats(bean_id=1, average_rating=4.0, review_count=2),
        BeanStats(bean_id=3, average_rating=4.5, review_count=1),
        BeanStats(bean_id=4, average_rating=4.0, review_count=5),
    ]
    client = use_fakes(FakeCatalog(beans), FakeReviews(stats=stats))
    body = client.get("/api/insights/leaderboard").json()
    assert [b["bean_id"] for b in body] == [3, 4, 1, 2]
    assert body[-1]["average_rating"] is None
    assert body[-1]["review_count"] == 0


def test_leaderboard_limit(use_fakes):
    beans = [make_bean(i, f"B{i}") for i in range(1, 5)]
    client = use_fakes(FakeCatalog(beans), FakeReviews())
    assert len(client.get("/api/insights/leaderboard?limit=2").json()) == 2
    assert client.get("/api/insights/leaderboard?limit=0").status_code == 422
    assert client.get("/api/insights/leaderboard?limit=21").status_code == 422


def test_bean_summary(use_fakes):
    reviews = [make_review(i, 1, r) for i, r in enumerate([5, 4, 4, 3])]
    client = use_fakes(FakeCatalog([make_bean(1, "A")]), FakeReviews(reviews))
    body = client.get("/api/insights/beans/1").json()
    assert body["bean"]["name"] == "A"
    assert body["review_count"] == 4
    assert body["average_rating"] == 4.0
    assert len(body["latest_reviews"]) == 3


def test_bean_summary_without_reviews(use_fakes):
    client = use_fakes(FakeCatalog([make_bean(1, "A")]), FakeReviews())
    body = client.get("/api/insights/beans/1").json()
    assert body["average_rating"] is None
    assert body["review_count"] == 0
    assert body["latest_reviews"] == []


def test_bean_summary_not_found(use_fakes):
    response = use_fakes(FakeCatalog(), FakeReviews()).get("/api/insights/beans/99")
    assert response.status_code == 404
    assert response.json() == {"detail": "Bean not found"}


def test_upstream_unreachable_returns_502(use_fakes):
    client = use_fakes(FakeCatalog([make_bean(1, "A")]), FakeReviews(fail=True))
    assert client.get("/api/insights/beans/1").status_code == 502
    assert client.get("/api/insights/leaderboard").status_code == 502
    client = use_fakes(FakeCatalog(fail=True), FakeReviews())
    assert client.get("/api/insights/beans/1").status_code == 502


def test_leaderboard_upstream_not_found_returns_502(use_fakes):
    client = use_fakes(FakeCatalog(missing=True), FakeReviews())
    response = client.get("/api/insights/leaderboard")
    assert response.status_code == 502
    assert "detail" in response.json()
    client = use_fakes(FakeCatalog([make_bean(1, "A")]), FakeReviews(missing=True))
    response = client.get("/api/insights/leaderboard")
    assert response.status_code == 502
    assert "detail" in response.json()


def test_malformed_upstream_body_returns_502(use_fakes):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.startswith("/api/catalog"):
            return httpx.Response(200, text="<html>not json</html>")
        return httpx.Response(200, json=[{"bean_id": "x"}])

    transport = httpx.MockTransport(handler)
    catalog = CatalogClient("http://catalog", transport=transport)
    reviews = ReviewsClient("http://reviews", transport=transport)
    client = use_fakes(catalog, reviews)
    assert client.get("/api/insights/leaderboard").status_code == 502
    assert client.get("/api/insights/beans/1").status_code == 502
    # catalog fine, reviews payload has wrong shape
    good = make_bean(1, "A").model_dump(mode="json")
    transport2 = httpx.MockTransport(
        lambda r: httpx.Response(200, json=[good] if r.url.path.endswith("beans") else [{"bean_id": "x"}])
    )
    client = use_fakes(
        CatalogClient("http://catalog", transport=transport2),
        ReviewsClient("http://reviews", transport=transport2),
    )
    assert client.get("/api/insights/leaderboard").status_code == 502
