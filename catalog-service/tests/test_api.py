import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db, seed
from app.main import app


@pytest.fixture()
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, expire_on_commit=False)
    with TestingSession() as session:
        seed(session)

    def override_get_db():
        with TestingSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_list_beans_ordered_by_name(client):
    beans = client.get("/api/catalog/beans").json()
    assert len(beans) == 6
    assert [b["name"] for b in beans] == sorted(b["name"] for b in beans)


def test_list_beans_filtered_by_roast(client):
    beans = client.get("/api/catalog/beans", params={"roast": "dark"}).json()
    assert {b["name"] for b in beans} == {"Sumatra Mandheling", "Brazil Cerrado"}
    assert client.get("/api/catalog/beans", params={"roast": "burnt"}).status_code == 422


def test_get_bean_and_not_found(client):
    bean = client.get("/api/catalog/beans/1").json()
    assert bean["name"] == "Ethiopia Yirgacheffe"
    assert bean["price_cents"] == 1850
    missing = client.get("/api/catalog/beans/999")
    assert missing.status_code == 404
    assert missing.json() == {"detail": "Bean not found"}


def test_create_bean(client):
    payload = {
        "name": "Rwanda Nyungwe",
        "roaster": "Little Kiln",
        "origin": "Rwanda",
        "roast": "light",
        "price_cents": 1900,
    }
    response = client.post("/api/catalog/beans", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 7
    assert body["flavor_notes"] == ""
    assert body["created_at"]


def test_create_bean_rejects_non_positive_price(client):
    payload = {
        "name": "X",
        "roaster": "Y",
        "origin": "Z",
        "roast": "dark",
        "price_cents": 0,
    }
    assert client.post("/api/catalog/beans", json=payload).status_code == 422


def test_patch_bean_partial_update(client):
    response = client.patch("/api/catalog/beans/2", json={"price_cents": 1750})
    assert response.status_code == 200
    body = response.json()
    assert body["price_cents"] == 1750
    assert body["name"] == "Colombia Huila"
    missing = client.patch("/api/catalog/beans/999", json={"price_cents": 1})
    assert missing.status_code == 404
