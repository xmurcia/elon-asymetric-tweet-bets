# Asymetric Elon Bets App

Dashboard Polymarket Elon tweets.

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

## Features
- Gauss model
- Bursts heatmap
- Paper trading
- Tips webhook endpoints: `/api/tips/*`
