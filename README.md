# Asymetric Elon Bets App

Dashboard / webapp experimental para mercados Polymarket centrados en Elon.

## Estado real del repo
Hoy el repo está **más avanzado en backend que en UX de producto**:
- Backend oficial en progreso: `fastapi_backend/` con sync de datos de Gamma a Postgres y endpoints `/health`, `/events`, `/events/{id}/snapshots`, `/events/{id}/predictions`, `/coverage`.
- Frontend actual: shell React + RainbowKit para conectar wallet y lanzar una **demo tx de valor 0** en Polygon.
- Aún **no está cerrada** la demo interna móvil objetivo: faltan recomendación/stake en UI, histórico/accuracy visible y flujo real de tip en USDC end-to-end.
- El directorio `backend/` sigue presente como legado y no debe tratarse como fuente principal para el MVP actual.

## Local dev (frontend)
```bash
npm install --legacy-peer-deps
npm start
```

Open: http://localhost:3000

## Backend (FastAPI) + Postgres via Docker Compose
Prereqs: Docker.

```bash
cp .env.example .env  # optional; fill ALCHEMY_WEBHOOK_SECRET if you use webhooks
docker compose up --build
```

Backend:
- http://localhost:8000/
- http://localhost:8000/health
- http://localhost:8000/events
- http://localhost:8000/events/{id}/snapshots
- http://localhost:8000/events/{id}/predictions

Database:
- Postgres exposed on localhost:5432 (see docker-compose.yml credentials)

## E2E smoke test (Playwright)
One-time browser install:
```bash
npx playwright install --with-deps
```

Run:
```bash
npm run e2e
```

## Environment variables
- `DATABASE_URL` (required by backend)
- `ALCHEMY_WEBHOOK_SECRET` (required only for `/api/tips/webhook`)

Market data (Gamma):
- `GAMMA_API_BASE` (optional, default `https://gamma-api.polymarket.com`)
- `MARKET_QUERY` (optional filter, e.g. `elon`)
- `MARKET_LIMIT` (optional, default `50`)
- `SCHEDULER_ENABLED` (optional, default `true`)
- `MARKET_SYNC_INTERVAL_SECONDS` (optional, default `300`)

## Verify real market data coverage
After `docker compose up --build`, wait ~1 minute and check:
- http://localhost:8000/coverage

You should see:
- `events.total` > 0
- `buckets.expected` > 0
- `prices.latest_snapshot_at` not null
- `coverage_pct` > 0

## Backend smoke test
With the stack running locally:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/events
curl http://localhost:8000/coverage
```

Then pick one returned event id and verify:
```bash
curl http://localhost:8000/events/1/snapshots
curl http://localhost:8000/events/1/predictions
```

## Features
- Gauss model
- Bursts heatmap
- Paper trading
- Tips webhook endpoints: `/api/tips/*`
