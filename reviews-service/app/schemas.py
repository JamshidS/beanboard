from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ReviewCreate(BaseModel):
    author: str = Field(min_length=1, max_length=60)
    rating: int = Field(ge=1, le=5)
    comment: str = Field(default="", max_length=500)


class Review(BaseModel):
    id: str
    bean_id: int
    author: str
    rating: int = Field(ge=1, le=5)
    comment: str
    created_at: datetime

    @classmethod
    def from_doc(cls, doc: dict[str, Any]) -> "Review":
        return cls(
            id=str(doc["_id"]),
            bean_id=doc["bean_id"],
            author=doc["author"],
            rating=doc["rating"],
            comment=doc["comment"],
            created_at=doc["created_at"],
        )


class BeanStats(BaseModel):
    bean_id: int
    average_rating: float
    review_count: int
