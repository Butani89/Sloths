"""
Subscription service - handles validation and business logic for subscriptions.
This service sits between the presentation layer (routes) and the data layer
(repositories).
"""
import re
from app.data.repositories.subscriber_repository import SubscriberRepository

class SubscriptionService:
    """Service for handling subscription-related business logic."""

    EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    def __init__(self, repository: SubscriberRepository | None = None):
        """Initialize the subscription service with a repository."""
        self.repository = repository or SubscriberRepository()

    def validate_email(self, email: str) -> tuple[bool, str]:
        """Validate email format."""
        if not email or not email.strip():
            return False, "Email is required"
        if not re.match(self.EMAIL_PATTERN, email.strip()):
            return False, "Invalid email format"
        return True, ""

    def normalize_email(self, email: str) -> str:
        """Normalize email address."""
        return email.lower().strip()

    def normalize_name(self, name: str | None) -> str:
        """Normalize name field."""
        if not name or not name.strip():
            return "Subscriber"
        return name.strip()

    def subscribe(self, email: str, name: str | None) -> tuple[bool, str]:
        """
        Full subscription flow: validate, check duplicate, save.
        Returns: (success, error_message)
        """
        # Validate email format
        is_valid, error = self.validate_email(email)
        if not is_valid:
            return False, error

        # Normalize inputs
        normalized_email = self.normalize_email(email)
        normalized_name = self.normalize_name(name)

        # Check for duplicate subscription
        if self.repository.exists(normalized_email):
            return False, "This email is already subscribed"

        # Save to database
        self.repository.create(email=normalized_email, name=normalized_name)

        return True, ""