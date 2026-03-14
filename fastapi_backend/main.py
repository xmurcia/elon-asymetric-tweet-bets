import logging

from fastapi import FastAPI

from .metrics import Metrics, MetricsMiddleware
from .scheduler import init_scheduler
from .webhooks import router as tips_router

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Elon Asymmetric Tweet Bets API")

# Lightweight in-memory metrics (for basic monitoring/debugging)
metrics = Metrics()
app.add_middleware(MetricsMiddleware, metrics=metrics)

# BACKEND-JOBS-002: start APScheduler via proper FastAPI lifecycle hooks
init_scheduler(app)

app.include_router(tips_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Elon Asymmetric Tweet Bets API!"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def get_metrics():
    return metrics.snapshot()
