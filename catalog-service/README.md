# Catalog Service

A FastAPI service that stores the Beanboard catalog of specialty coffee beans in PostgreSQL.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/catalog/beans` | List beans ordered by name, optional `roast` filter (`light`, `medium`, `dark`) |
| GET | `/api/catalog/beans/{bean_id}` | Get one bean, 404 if missing |
| POST | `/api/catalog/beans` | Create a bean (201) |
| PATCH | `/api/catalog/beans/{bean_id}` | Partially update a bean, 404 if missing |
| GET | `/health` | Liveness check |

On startup the `beans` table is created and seeded with 6 beans if it is empty.

## Environment variables

| Name | Default |
| --- | --- |
| `DATABASE_URL` | `postgresql+psycopg2://beanboard:beanboard@localhost:5432/catalog` |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:8080` |

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

## Test

Tests use an in-memory SQLite database, no PostgreSQL needed.

```bash
pip install -r requirements-dev.txt
pytest
```
