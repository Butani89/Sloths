"""Authentication service - handles user authentication and management.
This service sits in the business layer, coordinating between the
presentation layer (routes) and the data layer (User model).
"""
from sqlalchemy.exc import IntegrityError
from app import db
from app.data.models.user import User

class DuplicateUsernameError(Exception):
    """Raised when attempting to create a user with an existing username."""
    pass

class AuthService:
    """Service for authentication-related business logic."""

    @staticmethod
    def authenticate(username, password):
        """
        Authenticate a user by username and password.
        Checks that the user exists, is active, and the password matches.

        Args:
            username: The username to authenticate
            password: The plain text password to verify

        Returns:
            User instance if authentication succeeds, None otherwise
        """
        user = User.query.filter_by(username=username).first()
        if user and user.is_active and user.check_password(password):
            return user
        return None

    @staticmethod
    def create_user(username, password):
        """
        Create a new user with hashed password.

        Args:
            username: Unique username for the new user
            password: Plain text password (will be hashed)

        Returns:
            The newly created User instance

        Raises:
            DuplicateUsernameError: If username already exists
        """
        user = User(username=username)
        user.set_password(password)
        try:
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            raise DuplicateUsernameError(f"Username '{username}' already exists.")

    @staticmethod
    def get_user_by_id(user_id):
        """
        Get a user by their database ID.
        Used by Flask-Login's user_loader callback.

        Args:
            user_id: The user's database ID (as string or int)

        Returns:
            User instance if found, None otherwise
        """
        return db.session.get(User, int(user_id))