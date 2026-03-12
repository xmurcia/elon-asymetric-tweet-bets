import hmac
import hashlib
import os
import datetime
from fastapi import APIRouter, Request, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func # Import func for sum
from dotenv import load_dotenv

from .database import SessionLocal, engine
from .models import Tip, Base

# Load environment variables
load_dotenv()

# Ensure tables are created
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/api/tips")

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Alchemy webhook secret from environment variables
ALCHEMY_WEBHOOK_SECRET = os.getenv("ALCHEMY_WEBHOOK_SECRET")
USDC_CONTRACT_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174" # Polygon mainnet USDC

@router.post("/webhook")
async def alchemy_webhook(request: Request, db: Session = Depends(get_db)):
    if not ALCHEMY_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Alchemy webhook secret not configured.")

    # 1. Verify Alchemy signature
    signature = request.headers.get("X-Alchemy-Signature")
    if not signature:
        raise HTTPException(status_code=400, detail="X-Alchemy-Signature header missing.")

    body = await request.body()
    calculated_signature = hmac.new(
        ALCHEMY_WEBHOOK_SECRET.encode('utf-8'),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, calculated_signature):
        raise HTTPException(status_code=403, detail="Invalid Alchemy signature.")

    # 2. Parse transaction data and validate USDC contract
    try:
        data = await request.json()
        print(f"Received webhook data: {data}") # Log incoming data for debugging
        # Assuming only one event for simplicity, adjust for multiple if needed
        event = data['event']['activity'][0] # Alchemy activity webhook structure
        
        # Check if the event is a USDC transfer to our contract
        if event['rawContract']['address'].lower() != USDC_CONTRACT_ADDRESS.lower():
            return {"message": "Not a USDC transfer to the monitored contract, ignoring."}

        # Extract relevant data
        from_address = event['fromAddress']
        to_address = event['toAddress']
        value_wei = int(event['value'], 16) # Value is in wei, needs conversion
        value_usdc = value_wei / (10**6) # USDC has 6 decimals

        # For tips, we assume the 'to_address' is the recipient of the tip.
        # The 'from_address' is the sender.
        # Alchemy webhooks provide 'value' and 'asset' for transfers.
        # We also need transaction hash and timestamp.
        transaction_hash = event['hash']
        block_timestamp = event['blockNum'] # This might be block number, not timestamp, needs adjustment if real timestamp is required.
                                            # Alchemy typically provides 'timestamp' if it's a 'MINED_TRANSACTION' webhook.
                                            # For 'ADDRESS_ACTIVITY' webhooks, 'blockNum' is common.
                                            # We may need to fetch block details for actual timestamp or adjust model.
        
        # For simplicity, using a placeholder for timestamp or re-evaluating data structure.
        # Let's assume 'blockNum' can be used as a unique identifier for now, or we get a proper timestamp from 'data'.
        # Alchemy's 'activity' has a 'timestamp' field for actual time, not just block number.
        # Let's check if 'data['event']['activity'][0]['blockNum']' should be 'data['event']['activity'][0]['metadata']['blockTimestamp']'.
        # For now, I'll use a placeholder for timestamp in the model and refine it after testing.
        import datetime
        timestamp = datetime.datetime.now() # Placeholder for now, to be replaced by actual transaction timestamp
                                           # A proper Alchemy webhook for transfers would have 'log.block.timestamp' or similar.
        
        # 3. Persist tips confirmed in tabla `tips` de BD
        new_tip = Tip(
            sender_address=from_address,
            amount=value_usdc,
            timestamp=timestamp,
            transaction_hash=transaction_hash,
            is_confirmed=True # Webhook confirmation means it's confirmed
        )
        db.add(new_tip)
        db.commit()
        db.refresh(new_tip)

        return {"message": "Tip received and processed successfully!", "tip_id": new_tip.id}

    except Exception as e:
        print(f"Error processing webhook: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing webhook: {e}")

@router.get("/recent")
async def get_recent_tips(db: Session = Depends(get_db)):
    # Return last 10 tips (anonymous)
    recent_tips = db.query(Tip).order_by(Tip.timestamp.desc()).limit(10).all()
    # You might want to return a subset of information, or anonymize sender_address
    return [
        {
            "amount": str(tip.amount), 
            "timestamp": tip.timestamp.isoformat(), 
            "transaction_hash": tip.transaction_hash
        } 
        for tip in recent_tips
    ]

@router.get("/stats")
async def get_tip_stats(db: Session = Depends(get_db)):
    # Return total count, total amount, etc
    total_tips_count = db.query(Tip).count()
    total_amount_result = db.query(func.sum(Tip.amount)).scalar()
    total_amount = total_amount_result if total_amount_result is not None else 0



    return {
        "total_tips_count": total_tips_count,
        "total_amount_usdc": str(total_amount)
    }
