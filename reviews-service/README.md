# Reviews Service

A FastAPI service that stores tasting reviews for Beanboard coffee beans in MongoDB and aggregates rating stats per bean.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/reviews/beans/{bean_id}` | List reviews for a bean, newest first |
| POST | `/api/reviews/beans/{bean_id}` | Add a review, rating 1 to 5. Checks the bean exists in catalog-service first. Returns 201 on success, 404 `Bean not found` if the bean does not exist, 502 `Catalog service unavailable, please try again later` if catalog-service is unreachable, times out or answers with an error (the cause is logged), 422 for an invalid body (no catalog call, nothing stored) |
| DELETE | `/api/reviews/{review_id}` | Delete a review (204), 404 if missing or id is invalid |
| GET | `/api/reviews/stats` | Average rating and review count for every bean that has reviews |
| GET | `/health` | Liveness check |

On startup an index on `bean_id` is created and about 10 demo reviews are seeded if the collection is empty.

## Environment variables

| Name | Default |
| --- | --- |
| `MONGO_URL` | `mongodb://localhost:27017` |
| `MONGO_DB` | `reviews` |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:8080` |
| `CATALOG_SERVICE_URL` | `http://localhost:8001` |
| `REQUEST_TIMEOUT` | `5` (seconds, for calls to catalog-service) |

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

## Test

Tests use `mongomock`, no MongoDB needed.

```bash
pip install -r requirements-dev.txt
pytest
```
