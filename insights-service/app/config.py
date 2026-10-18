import os

CATALOG_SERVICE_URL = os.getenv("CATALOG_SERVICE_URL", "http://localhost:8001")
REVIEWS_SERVICE_URL = os.getenv("REVIEWS_SERVICE_URL", "http://localhost:8002")
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:8080"
    ).split(",")
    if origin.strip()
]
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "5"))
