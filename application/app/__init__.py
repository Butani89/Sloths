"""
News Flash - Application Factory
This module creates and configures the Flask application.
"""
import os
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from .config import config

# Create extensions at module level (initialized in create_app)
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name: str | None = None) -> Flask:
    """
    Create and configure the Flask application.
    """
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    app = Flask(
        __name__,
        template_folder="presentation/templates",
        static_folder="presentation/static",
    )

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models (after db.init_app to avoid circular imports)
    from .data import models  # noqa: F401
    from app.data.models.user import User  # noqa: F401

    # Register blueprints
    from .presentation.routes.public import bp as public_bp
    app.register_blueprint(public_bp)

    from .presentation.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    return app