from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException, Response
from pymongo import DESCENDING
from pymongo.collection import Collection

from app.catalog import (
    CATALOG_UNAVAILABLE_DETAIL,
    CatalogClient,
    UpstreamError,
    get_catalog_client,
)
from app.db import get_collection
from app.schemas import BeanStats, Review, ReviewCreate

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("/stats", response_model=list[BeanStats])
def review_stats(collection: Collection = Depends(get_collection)):
    pipeline = [
        {
            "$group": {
                "_id": "$bean_id",
                "average_rating": {"$avg": "$rating"},
                "review_count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    return [
        BeanStats(
            bean_id=row["_id"],
            average_rating=round(row["average_rating"], 2),
            review_count=row["review_count"],
        )
        for row in collection.aggregate(pipeline)
    ]


@router.get("/beans/{bean_id}", response_model=list[Review])
def list_reviews(bean_id: int, collection: Collection = Depends(get_collection)):
    docs = collection.find({"bean_id": bean_id}).sort(
        [("created_at", DESCENDING), ("_id", DESCENDING)]
    )
    return [Review.from_doc(doc) for doc in docs]


@router.post("/beans/{bean_id}", response_model=Review, status_code=201)
def create_review(
    bean_id: int,
    payload: ReviewCreate,
    collection: Collection = Depends(get_collection),
    catalog: CatalogClient = Depends(get_catalog_client),
):
    # Runs only after the body validated (422 otherwise), so no upstream call then.
    try:
        exists = catalog.bean_exists(bean_id)
    except UpstreamError as exc:
        # The cause is logged by app.catalog; the client gets a fixed message.
        raise HTTPException(status_code=502, detail=CATALOG_UNAVAILABLE_DETAIL) from exc
    if not exists:
        raise HTTPException(status_code=404, detail="Bean not found")
    doc = {
        "bean_id": bean_id,
        **payload.model_dump(),
        "created_at": datetime.now(timezone.utc),
    }
    doc["_id"] = collection.insert_one(doc).inserted_id
    return Review.from_doc(doc)


@router.delete("/{review_id}", status_code=204)
def delete_review(review_id: str, collection: Collection = Depends(get_collection)):
    try:
        object_id = ObjectId(review_id)
    except InvalidId:
        raise HTTPException(status_code=404, detail="Review not found")
    if collection.delete_one({"_id": object_id}).deleted_count == 0:
        raise HTTPException(status_code=404, detail="Review not found")
    return Response(status_code=204)
