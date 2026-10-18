# Beanboard UI

A React + TypeScript single-page app for browsing specialty coffee beans, reading and writing tasting reviews, and seeing the top-rated leaderboard.

## Run in development

```bash
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api/catalog`, `/api/reviews` and `/api/insights` to the backend services on ports 8001, 8002 and 8003.

## Build

```bash
npm run build     # type-check and bundle into dist/
npm run preview   # serve the production build locally
```

## Docker

The Dockerfile builds the app and serves `dist/` with nginx on port 80. `nginx.conf` proxies `/api/catalog/`, `/api/reviews/` and `/api/insights/` to the matching services (no path stripping) and falls back to `index.html` for client-side routes.

## Layout

- `src/api.ts` holds every backend call, one function per endpoint.
- `src/types.ts` mirrors the pydantic schemas.
- `src/pages/` has the beans list (`/`) and bean detail (`/beans/:beanId`) pages.
- `src/components/` has the small shared components.
