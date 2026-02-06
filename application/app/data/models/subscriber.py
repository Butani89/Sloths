"""
Subscriber model - represents a newsletter subscriber.
This model belongs to the Data Layer and defines the database schema.
"""
from datetime import datetime, timezone
from app import db

class Subscriber(db.Model):
    """
    Newsletter subscriber.
    """
    __tablename__ = "subscribers"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, default="Subscriber")
    subscribed_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Subscriber {self.email}>"