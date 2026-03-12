from fastapi import FastAPI
from .webhooks import router as tips_router

app = FastAPI()

app.include_router(tips_router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Elon Asymmetric Tweet Bets API!"}
