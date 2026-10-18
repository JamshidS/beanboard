import mongomock
import pytest
from fastapi.testclient import TestClient

from app.db import get_collection, seed
from app.main import app


@pytest.fixture()
def collection():
    return mongomock.MongoClient(tz_aware=True)["reviews"]["reviews"]


@pytest.fixture()
def client(collection):
    app.dependency_overrides[get_collection] = lambda: collection
    yield TestClient(app)
    app.dependency_overrides.clear()


def post_review(client, bean_id, author="Ana", rating=5, comment="Great"):
    return client.post(
        f"/api/reviews/beans/{bean_id}",
        json={"author": author, "rating": rating, "comment": comment},
    )


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_create_and_list_reviews_newest_first(client):
    first = post_review(client, 1, author="Ana", rating=4)
    assert first.status_code == 201
    assert first.json()["bean_id"] == 1
    post_review(client, 1, author="Marco", rating=2)
    post_review(client, 2, author="Leo", rating=5)

    reviews = client.get("/api/reviews/beans/1").json()
    assert [r["author"] for r in reviews] == ["Marco", "Ana"]
    assert client.get("/api/reviews/beans/99").json() == []


def test_create_review_validation(client):
    assert post_review(client, 1, rating=6).status_code == 422
    assert post_review(client, 1, rating=0).status_code == 422
    assert post_review(client, 1, author="").status_code == 422
    assert post_review(client, 1, comment="x" * 501).status_code == 422
    default = client.post("/api/reviews/beans/1", json={"author": "Ana", "rating": 3})
    assert default.status_code == 201
    assert default.json()["comment"] == ""


def test_delete_review(client):
    review_id = post_review(client, 1).json()["id"]
    assert client.delete(f"/api/reviews/{review_id}").status_code == 204
    assert client.get("/api/reviews/beans/1").json() == []
    again = client.delete(f"/api/reviews/{review_id}")
    assert again.status_code == 404
    assert again.json() == {"detail": "Review not found"}


def test_delete_invalid_object_id_is_404(client):
    response = client.delete("/api/reviews/not-an-object-id")
    assert response.status_code == 404
    assert response.json() == {"detail": "Review not found"}


def test_stats_aggregates_per_bean(client):
    post_review(client, 1, rating=5)
    post_review(client, 1, rating=4)
    post_review(client, 1, rating=4)
    post_review(client, 3, rating=2)

    stats = {s["bean_id"]: s for s in client.get("/api/reviews/stats").json()}
    assert set(stats) == {1, 3}
    assert stats[1]["average_rating"] == 4.33
    assert stats[1]["review_count"] == 3
    assert stats[3] == {"bean_id": 3, "average_rating": 2.0, "review_count": 1}


def test_seed_populates_empty_collection_once(collection):
    seed(collection)
    count = collection.count_documents({})
    assert count >= 10
    assert collection.count_documents({"bean_id": 6}) == 0
    seed(collection)
    assert collection.count_documents({}) == count
