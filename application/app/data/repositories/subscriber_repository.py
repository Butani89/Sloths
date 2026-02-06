"""
Subscriber repository - handles database operations for subscribers.
This repository encapsulates all SQLAlchemy queries for the Subscriber model.
"""
from app import db
from app.data.models.subscriber import Subscriber

class SubscriberRepository:
    """
    Data access layer for Subscriber operations.
    """

    def find_by_email(self, email: str) -> Subscriber | None:
        """Find a subscriber by email address."""
        return Subscriber.query.filter_by(email=email.lower()).first()

    def exists(self, email: str) -> bool:
        """Check if a subscriber with the given email exists."""
        return self.find_by_email(email) is not None

    def create(self, email: str, name: str) -> Subscriber:
        """Create a new subscriber."""
        subscriber = Subscriber(email=email, name=name)
        db.session.add(subscriber)
        db.session.commit()
        return subscriber