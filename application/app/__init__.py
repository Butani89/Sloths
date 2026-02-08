"""
News Flash - Application Factory
This module creates and configures the Flask application.
"""
import os
# OBS: Lade till render_template här
from flask import Flask, render_template
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import config

# Create extensions at module level (initialized in create_app)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

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
    
    # Initialize Flask-Login
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        from app.business.services.auth_service import AuthService
        return AuthService.get_user_by_id(user_id)

    # Import models (after db.init_app to avoid circular imports)
    from .data import models  # noqa: F401
    from app.data.models.user import User  # noqa: F401

    # Register blueprints
    from .presentation.routes.public import bp as public_bp
    app.register_blueprint(public_bp)

    from .presentation.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from .presentation.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Add security headers (Step 1 - Security Headers Middleware)
    @app.after_request
    def add_security_headers(response):
        """Add OWASP-recommended security headers to all responses."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        # HSTS only in production (not during development/testing)
        if not app.debug and not app.testing:
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        return response

    # Register CLI commands (Step 2)
    from app.cli import create_admin_command
    app.cli.add_command(create_admin_command)

    # Register Error Handlers (Step 3)
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    return app