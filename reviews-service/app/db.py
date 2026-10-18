from datetime import datetime, timedelta, timezone

from pymongo import MongoClient
from pymongo.collection import Collection

from app.config import MONGO_DB, MONGO_URL

client = MongoClient(MONGO_URL, tz_aware=True)

# (bean_id, author, rating, comment); bean 6 intentionally has no reviews.
SEED_REVIEWS = [
    (1, "Ana", 5, "Floral and bright, like iced jasmine tea with a lemon twist."),
    (1, "Marco", 4, "Lovely bergamot aroma, a little sharp as espresso."),
    (2, "Priya", 4, "Balanced and easy. Red apple up front, caramel finish."),
    (2, "Leo", 3, "Pleasant but forgettable as a daily drinker."),
    (3, "Ana", 5, "Juicy blackcurrant, the best filter coffee I had this year."),
    (3, "Leo", 4, "Wild and fruity. The tomato note is real, in a good way."),
    (4, "Marco", 3, "Heavy and earthy, great with milk, too smoky black."),
    (4, "Priya", 2, "Too much cedar for my taste."),
    (5, "Leo", 4, "Smooth milk chocolate, perfect for mornings."),
    (5, "Ana", 5, "Orange zest and almond, my go-to pour-over."),
]


def get_collection() -> Collection:
    return client[MONGO_DB]["reviews"]


def seed(collection: Collection) -> None:
    """Insert the demo reviews if the collection is empty."""
    if collection.count_documents({}) > 0:
        return
    now = datetime.now(timezone.utc)
    total = len(SEED_REVIEWS)
    collection.insert_many(
        {
            "bean_id": bean_id,
            "author": author,
            "rating": rating,
            "comment": comment,
            "created_at": now - timedelta(days=total - index, hours=index),
        }
        for index, (bean_id, author, rating, comment) in enumerate(SEED_REVIEWS)
    )


def init_db() -> None:
    collection = get_collection()
    collection.create_index("bean_id")
    seed(collection)
