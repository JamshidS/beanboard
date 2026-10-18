from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    sessionmaker,
)

from app.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


class BeanRow(Base):
    __tablename__ = "beans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    roaster: Mapped[str] = mapped_column(String(120))
    origin: Mapped[str] = mapped_column(String(80))
    roast: Mapped[str] = mapped_column(String(10))
    price_cents: Mapped[int] = mapped_column(Integer)
    flavor_notes: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

SEED_BEANS = [
    ("Ethiopia Yirgacheffe", "Northbound Roasters", "Ethiopia", "light", 1850, "jasmine, bergamot, lemon"),
    ("Colombia Huila", "Northbound Roasters", "Colombia", "medium", 1600, "red apple, caramel, cocoa"),
    ("Kenya Nyeri AA", "Ember & Oak", "Kenya", "light", 2100, "blackcurrant, grapefruit, tomato"),
    ("Sumatra Mandheling", "Ember & Oak", "Indonesia", "dark", 1500, "cedar, dark chocolate, earthy"),
    ("Guatemala Antigua", "Little Kiln", "Guatemala", "medium", 1700, "milk chocolate, almond, orange"),
    ("Brazil Cerrado", "Little Kiln", "Brazil", "dark", 1300, "peanut, molasses, low acidity"),
]


def get_db():
    with SessionLocal() as session:
        yield session


def seed(session: Session) -> None:
    """Insert the demo beans if the table is empty."""
    if session.scalar(select(BeanRow.id).limit(1)) is not None:
        return
    session.add_all(
        BeanRow(
            name=name,
            roaster=roaster,
            origin=origin,
            roast=roast,
            price_cents=price_cents,
            flavor_notes=flavor_notes,
        )
        for name, roaster, origin, roast, price_cents, flavor_notes in SEED_BEANS
    )
    session.commit()


def init_db() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as session:
        seed(session)
