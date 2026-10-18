# Beanboard Insights Service

Combines catalog and review data over HTTP to serve the Beanboard leaderboard and per-bean summaries (no database of its own).

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/insights/leaderboard?limit=5` | All beans with their rating, best first, unrated last (`limit` 1..20) |
| GET | `/api/insights/beans/{bean_id}` | Bean, average rating, review count and the 3 latest reviews |
| GET | `/health` | Liveness check |

`/api/insights/beans/{bean_id}` returns 404 if the bean does not exist and 502 if catalog or reviews is unreachable.

## Environment variables

| Variable | Default |
| --- | --- |
| `CATALOG_SERVICE_URL` | `http://localhost:8001` |
| `REVIEWS_SERVICE_URL` | `http://localhost:8002` |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:8080` |
| `REQUEST_TIMEOUT` | `5` (seconds) |

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
```

Docs: http://localhost:8003/docs

## Test

```bash
pip install -r requirements-dev.txt
pytest
```

Tests use fake clients via FastAPI dependency overrides, so no other service is needed.
