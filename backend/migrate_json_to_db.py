import json
import os
from datetime import datetime
from backend.database import SessionLocal, Event, BucketSnapshot, ModelPrediction, Tip

def migrate_data(json_file_path: str):
    db = SessionLocal()
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)

        for event_data in data:
            # Create Event
            event = Event(
                tweet_id=event_data["tweet_id"],
                tweet_text=event_data["tweet_text"],
                tweet_author_id=event_data["tweet_author_id"],
                tweet_created_at=datetime.fromisoformat(event_data["tweet_created_at"]) if isinstance(event_data["tweet_created_at"], str) else event_data["tweet_created_at"],
                event_type=event_data["event_type"],
                created_at=datetime.utcnow() # Assuming creation now
            )
            db.add(event)
            db.flush() # Flush to get event.id

            # Create ModelPrediction (if exists)
            if "model_prediction" in event_data:
                prediction_data = event_data["model_prediction"]
                model_prediction = ModelPrediction(
                    event_id=event.id,
                    model_name=prediction_data["model_name"],
                    prediction_value=prediction_data["prediction_value"],
                    prediction_timestamp=datetime.fromisoformat(prediction_data["prediction_timestamp"]) if isinstance(prediction_data["prediction_timestamp"], str) else prediction_data["prediction_timestamp"],
                    is_correct=prediction_data.get("is_correct"),
                    confidence=prediction_data.get("confidence")
                )
                db.add(model_prediction)
                event.prediction_id = model_prediction.id # Link prediction to event

            # Create BucketSnapshots (if exists)
            if "bucket_snapshots" in event_data:
                for snapshot_data in event_data["bucket_snapshots"]:
                    bucket_snapshot = BucketSnapshot(
                        event_id=event.id,
                        bucket_type=snapshot_data["bucket_type"],
                        bucket_name=snapshot_data["bucket_name"],
                        value=snapshot_data["value"],
                        timestamp=datetime.fromisoformat(snapshot_data["timestamp"]) if isinstance(snapshot_data["timestamp"], str) else snapshot_data["timestamp"],
                    )
                    db.add(bucket_snapshot)

            # Create Tips (if exists)
            if "tips" in event_data:
                for tip_data in event_data["tips"]:
                    tip = Tip(
                        event_id=event.id,
                        user_id=tip_data["user_id"],
                        tip_value=tip_data["tip_value"],
                        tip_currency=tip_data["tip_currency"],
                        tipped_at=datetime.fromisoformat(tip_data["tipped_at"]) if isinstance(tip_data["tipped_at"], str) else tip_data["tipped_at"],
                    )
                    db.add(tip)
        db.commit()
        print(f"Successfully migrated data from {json_file_path}")
    except Exception as e:
        db.rollback()
        print(f"Error during migration: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    # Example usage: Assumes a JSON file named data.json in the same directory
    # You should adapt this to your actual data source.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(current_dir, "data.json") # Placeholder for the actual JSON file

    # Create a dummy data.json for testing if it doesn't exist
    if not os.path.exists(json_file):
        dummy_data = [
            {
                "tweet_id": "1234567890",
                "tweet_text": "Elon Musk tweet about Dogecoin - very good!",
                "tweet_author_id": "elonmusk",
                "tweet_created_at": "2023-01-01T12:00:00",
                "event_type": "doge_prediction",
                "model_prediction": {
                    "model_name": "price_predictor_v1",
                    "prediction_value": 0.08,
                    "prediction_timestamp": "2023-01-01T12:05:00",
                    "is_correct": None,
                    "confidence": 0.9
                },
                "bucket_snapshots": [
                    {
                        "bucket_type": "price",
                        "bucket_name": "doge_usdt",
                        "value": 0.075,
                        "timestamp": "2023-01-01T12:00:10"
                    },
                    {
                        "bucket_type": "sentiment",
                        "bucket_name": "tweet_sentiment",
                        "value": 0.8,
                        "timestamp": "2023-01-01T12:00:15"
                    }
                ],
                "tips": [
                    {
                        "user_id": "user1",
                        "tip_value": 10.0,
                        "tip_currency": "MSK",
                        "tipped_at": "2023-01-01T12:10:00"
                    }
                ]
            },
            {
                "tweet_id": "9876543210",
                "tweet_text": "New factory opening soon!",
                "tweet_author_id": "elonmusk",
                "tweet_created_at": "2023-01-02T09:00:00",
                "event_type": "announcement",
                "model_prediction": {
                    "model_name": "engagement_predictor_v2",
                    "prediction_value": 150000.0,
                    "prediction_timestamp": "2023-01-02T09:05:00",
                    "is_correct": True,
                    "confidence": 0.95
                },
                "bucket_snapshots": [],
                "tips": []
            }
        ]
        with open(json_file, 'w') as f:
            json.dump(dummy_data, f, indent=4)
        print("Created a dummy data.json for migration testing.")

    migrate_data(json_file)
