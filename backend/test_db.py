import unittest
from datetime import datetime
from backend.database import SessionLocal, Event, BucketSnapshot, ModelPrediction, Tip, get_db_engine, Base

class TestDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Use an in-memory SQLite database for testing
        # This ensures tests are isolated and don't affect the main database
        cls.engine = get_db_engine() # This will use the DATABASE_URL env var, which we ensure is test-specific
        Base.metadata.create_all(bind=cls.engine)
        cls.SessionLocal = SessionLocal

    @classmethod
    def tearDownClass(cls):
        Base.metadata.drop_all(bind=cls.engine)

    def setUp(self):
        self.db = self.SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_create_event(self):
        new_event = Event(
            tweet_id="test_tweet_1",
            tweet_text="This is a test tweet.",
            tweet_author_id="tester",
            tweet_created_at=datetime.utcnow(),
            event_type="test_event"
        )
        self.db.add(new_event)
        self.db.commit()
        self.db.refresh(new_event)
        self.assertIsNotNone(new_event.id)
        self.assertEqual(new_event.tweet_id, "test_tweet_1")

        retrieved_event = self.db.query(Event).filter(Event.tweet_id == "test_tweet_1").first()
        self.assertIsNotNone(retrieved_event)
        self.assertEqual(retrieved_event.tweet_author_id, "tester")

    def test_create_model_prediction(self):
        event = Event(
            tweet_id="pred_tweet_1",
            tweet_text="Prediction tweet.",
            tweet_author_id="pred_author",
            tweet_created_at=datetime.utcnow(),
            event_type="prediction_event"
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        prediction = ModelPrediction(
            event_id=event.id,
            model_name="test_model",
            prediction_value=0.75,
            prediction_timestamp=datetime.utcnow()
        )
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)

        self.assertIsNotNone(prediction.id)
        retrieved_prediction = self.db.query(ModelPrediction).filter(ModelPrediction.event_id == event.id).first()
        self.assertIsNotNone(retrieved_prediction)
        self.assertEqual(retrieved_prediction.prediction_value, 0.75)

    def test_create_bucket_snapshot(self):
        event = Event(
            tweet_id="snap_tweet_1",
            tweet_text="Snapshot tweet.",
            tweet_author_id="snap_author",
            tweet_created_at=datetime.utcnow(),
            event_type="snapshot_event"
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        snapshot = BucketSnapshot(
            event_id=event.id,
            bucket_type="price",
            bucket_name="BTC_USD",
            value=60000.50,
            timestamp=datetime.utcnow()
        )
        self.db.add(snapshot)
        self.db.commit()
        self.db.refresh(snapshot)

        self.assertIsNotNone(snapshot.id)
        retrieved_snapshot = self.db.query(BucketSnapshot).filter(BucketSnapshot.event_id == event.id).first()
        self.assertIsNotNone(retrieved_snapshot)
        self.assertEqual(retrieved_snapshot.value, 60000.50)

    def test_create_tip(self):
        event = Event(
            tweet_id="tip_tweet_1",
            tweet_text="Tip tweet.",
            tweet_author_id="tip_author",
            tweet_created_at=datetime.utcnow(),
            event_type="tip_event"
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        tip = Tip(
            event_id=event.id,
            user_id="user_alpha",
            tip_value=5.0,
            tip_currency="USD",
            tipped_at=datetime.utcnow()
        )
        self.db.add(tip)
        self.db.commit()
        self.db.refresh(tip)

        self.assertIsNotNone(tip.id)
        retrieved_tip = self.db.query(Tip).filter(Tip.user_id == "user_alpha").first()
        self.assertIsNotNone(retrieved_tip)
        self.assertEqual(retrieved_tip.tip_value, 5.0)

    def test_relationships(self):
        event = Event(
            tweet_id="rel_tweet_1",
            tweet_text="Relationship test.",
            tweet_author_id="rel_author",
            tweet_created_at=datetime.utcnow(),
            event_type="relationship_event"
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        prediction = ModelPrediction(
            event_id=event.id,
            model_name="rel_model",
            prediction_value=0.9,
            prediction_timestamp=datetime.utcnow()
        )
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)

        event.prediction_id = prediction.id
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        retrieved_event = self.db.query(Event).filter(Event.tweet_id == "rel_tweet_1").first()
        self.assertIsNotNone(retrieved_event.prediction)
        self.assertEqual(retrieved_event.prediction.model_name, "rel_model")


if __name__ == '__main__':
    # Ensure we use a test-specific database URL
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    unittest.main()
