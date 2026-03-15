import hmac
import hashlib
import os
import datetime
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from dotenv import load_dotenv

from .database import Base, SessionLocal, engine
from .models import Tip

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

    # 1) Verify Alchemy signature
    signature = request.headers.get("X-Alchemy-Signature")
    if not signature:
        raise HTTPException(status_code=400, detail="X-Alchemy-Signature header missing.")

    body = await request.body()
    calculated_signature = hmac.new(
        ALCHEMY_WEBHOOK_SECRET.encode("utf-8"),
        body,
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature, calculated_signature):
        raise HTTPException(status_code=403, detail="Invalid Alchemy signature.")

    # 2) Parse transaction data and validate USDC contract
    try:
        data = await request.json()

        activity = (data or {}).get("event", {}).get("activity", [])
        if not activity:
            raise HTTPException(status_code=400, detail="No activity entries in webhook payload.")

        # NOTE: currently processing only the first activity item.
        event = activity[0]

        raw_contract = (event or {}).get("rawContract", {})
        token_address = (raw_contract.get("address") or "").lower()
        if token_address != USDC_CONTRACT_ADDRESS.lower():
            return {"message": "Not a monitored USDC transfer; ignoring."}

        from_address = event.get("fromAddress")
        to_address = event.get("toAddress")
        if not from_address or not to_address:
            raise HTTPException(status_code=400, detail="Missing fromAddress/toAddress.")

        # Value may arrive as hex string (0x...) or decimal string
        raw_value = event.get("value")
        if raw_value is None:
            raise HTTPException(status_code=400, detail="Missing value.")
        if isinstance(raw_value, str) and raw_value.startswith("0x"):
            value_base_units = int(raw_value, 16)
        else:
            value_base_units = int(raw_value)

        value_usdc = value_base_units / (10**6)

        transaction_hash = event.get("hash")
        if not transaction_hash:
            raise HTTPException(status_code=400, detail="Missing tx hash.")

        # timestamp best-effort
        ts = None
        metadata = (event or {}).get("metadata", {})
        for k in ("blockTimestamp", "timestamp"):
            v = metadata.get(k) or event.get(k)
            if isinstance(v, str):
                try:
                    ts = datetime.datetime.fromisoformat(v.replace("Z", "+00:00"))
                    break
                except ValueError:
                    pass
        timestamp = ts or datetime.datetime.now(datetime.timezone.utc)

        # 3) Persist tip (idempotent by unique tx hash)
        new_tip = Tip(
            sender_address=from_address,
            amount=value_usdc,
            timestamp=timestamp,
            transaction_hash=transaction_hash,
            is_confirmed=True,
        )
        db.add(new_tip)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            return {"message": "Tip already processed.", "transaction_hash": transaction_hash}

        db.refresh(new_tip)
        return {"message": "Tip received and processed successfully!", "tip_id": new_tip.id}

    except HTTPException:
        raise
    except Exception as e:
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
