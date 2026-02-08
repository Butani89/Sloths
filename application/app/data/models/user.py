"""User model for admin authentication."""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    """Admin user with secure password storage.
    
    Passwords are hashed using Werkzeug's PBKDF2 implementation.
    Never stores plain text passwords.
    UserMixin provides Flask-Login integration:
    is_authenticated, is_active, is_anonymous, get_id()
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_password(self, password):
        """Hash and store a password.
        Args:
            password: Plain text password to hash
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify a password against the stored hash.
        Args:
            password: Plain text password to verify
        Returns:
            True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)