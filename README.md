# Beanboard

Beanboard is a small demo app where people browse specialty coffee beans, leave tasting reviews, and see a leaderboard of the best-rated beans.

It's the sandbox for **[aiset](https://github.com/JamshidS/aiset)**: three services, two databases and a UI, small enough to read in an afternoon and real enough for an AI team to find genuine bugs in.

## Try aiset on it

You need Docker, Python 3.9+, Git and [Claude Code](https://claude.com/claude-code).

```bash
git clone https://github.com/JamshidS/beanboard && cd beanboard
docker compose up --build -d                 # the app, on http://localhost:8080
pipx install aiset-cli                       # or: pip install aiset-cli
aiset-init . --team beanboard                # generates a PM, 4 engineers, QA and an integration checker
beanboard-pm                                 # talk to the PM
```

In a second terminal, run `aiset` and open http://127.0.0.1:8765 to watch the team.

Things to ask the PM:

1. *"Build the knowledge briefs."* Every engineer documents their service.
2. *"Can you do a quick bug analysis?"* The team reviews the services in parallel and reports ranked findings.
3. *"Let users sort the reviews."* A feature across UI and API, with clarifying questions first.

`main` is the untouched starting point, bugs included. The [`aiset-run`](https://github.com/JamshidS/beanboard/compare/main...aiset-run) branch has what the aiset team changed during the [recorded demo](https://github.com/JamshidS/aiset#a-real-run-start-to-finish): bean checks across services, upstream error handling, review sorting, and 26 new tests.

## Architecture

```
browser --> ui (React + nginx, :8080)
                |
                +--> insights (:8003) --+--> catalog (:8001) --> PostgreSQL
                |                       |
                +-----------------------+--> reviews (:8002) --> MongoDB
```

- **ui** calls insights for the leaderboard and bean summaries, and catalog and reviews directly for everything else (nginx proxies `/api/catalog`, `/api/reviews`, `/api/insights`).
- **catalog-service** owns the beans, stored in PostgreSQL.
- **reviews-service** owns the reviews, stored in MongoDB.
- **insights-service** has no database; it calls catalog and reviews over HTTP to build the leaderboard and bean summaries.

## Run it

```bash
docker compose up --build
```

Then open:

- UI: http://localhost:8080
- Catalog API docs: http://localhost:8001/docs
- Reviews API docs: http://localhost:8002/docs
- Insights API docs: http://localhost:8003/docs

Both databases are seeded with sample beans and reviews on first start.

## Local development

Start the databases with Docker, then run each service on its host port:

```bash
docker compose up postgres mongo
```

```bash
# catalog (http://localhost:8001)
cd catalog-service && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# reviews (http://localhost:8002)
cd reviews-service && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002

# insights (http://localhost:8003)
cd insights-service && pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003

# ui (http://localhost:5173, proxies /api to the ports above)
cd ui && npm install && npm run dev
```

Defaults for every setting are listed in `.env.example`.

## API

| Method | Path | Service | Description |
| --- | --- | --- | --- |
| GET | `/api/catalog/beans` | catalog | List beans by name, optional `roast` filter |
| GET | `/api/catalog/beans/{bean_id}` | catalog | Get one bean |
| POST | `/api/catalog/beans` | catalog | Create a bean |
| PATCH | `/api/catalog/beans/{bean_id}` | catalog | Partially update a bean |
| GET | `/api/reviews/beans/{bean_id}` | reviews | List a bean's reviews, newest first |
| POST | `/api/reviews/beans/{bean_id}` | reviews | Add a review |
| DELETE | `/api/reviews/{review_id}` | reviews | Delete a review |
| GET | `/api/reviews/stats` | reviews | Average rating and review count per reviewed bean |
| GET | `/api/insights/leaderboard` | insights | Beans ranked by average rating (`limit` 1..20, default 5) |
| GET | `/api/insights/beans/{bean_id}` | insights | Bean with rating summary and 3 latest reviews |

## Tests

Tests need no running databases or other services (SQLite in memory, mongomock, fake HTTP clients).

```bash
cd catalog-service && pip install -r requirements-dev.txt && pytest
cd reviews-service && pip install -r requirements-dev.txt && pytest
cd insights-service && pip install -r requirements-dev.txt && pytest
```
