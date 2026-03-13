import logging

from fastapi import FastAPI

from .scheduler import init_scheduler
from .webhooks import router as tips_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()

# BACKEND-JOBS-002: start APScheduler via proper FastAPI lifecycle hooks
init_scheduler(app)

app.include_router(tips_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Elon Asymmetric Tweet Bets API!"}
