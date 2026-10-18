from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Roast = Literal["light", "medium", "dark"]


class Bean(BaseModel):
    id: int
    name: str
    roaster: str
    origin: str
    roast: Roast
    price_cents: int
    flavor_notes: str
    created_at: datetime


class Review(BaseModel):
    id: str
    bean_id: int
    author: str
    rating: int
    comment: str
    created_at: datetime


class BeanStats(BaseModel):
    bean_id: int
    average_rating: float
    review_count: int


class BeanScore(BaseModel):
    bean_id: int
    name: str
    roaster: str
    roast: Roast
    average_rating: float | None
    review_count: int


class BeanSummary(BaseModel):
    bean: Bean
    average_rating: float | None
    review_count: int
    latest_reviews: list[Review] = Field(default_factory=list, max_length=3)
