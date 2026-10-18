from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Roast = Literal["light", "medium", "dark"]


class BeanCreate(BaseModel):
    name: str
    roaster: str
    origin: str
    roast: Roast
    price_cents: int = Field(gt=0)
    flavor_notes: str = ""


class BeanUpdate(BaseModel):
    name: str | None = None
    roaster: str | None = None
    origin: str | None = None
    roast: Roast | None = None
    price_cents: int | None = Field(default=None, gt=0)
    flavor_notes: str | None = None


class Bean(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    roaster: str
    origin: str
    roast: Roast
    price_cents: int
    flavor_notes: str
    created_at: datetime

    @field_validator("created_at")
    @classmethod
    def _ensure_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
