"""
Public routes - accessible without authentication.
This blueprint handles all public-facing pages including the landing page.
"""
from flask import Blueprint, render_template, request
from app.business.services.subscription_service import SubscriptionService

bp = Blueprint("public", __name__)

@bp.route("/")
def index():
    """Render the landing page."""
    return render_template("index.html")

@bp.route("/subscribe")
def subscribe():
    """Render the subscription form."""
    return render_template("subscribe.html")

@bp.route("/subscribe/confirm", methods=["POST"])
def subscribe_confirm():
    """Handle subscription form submission."""
    email = request.form.get("email", "")
    name = request.form.get("name", "")

    # Use business layer for full subscription flow
    service = SubscriptionService()
    success, error = service.subscribe(email, name)

    if not success:
        # Return to form with error message, preserving input
        return render_template(
            "subscribe.html",
            error=error,
            email=email,
            name=name,
        )

    # Subscription saved successfully - show thank you page
    # Use normalized values for display
    normalized_email = service.normalize_email(email)
    normalized_name = service.normalize_name(name)

    return render_template(
        "thank_you.html",
        email=normalized_email,
        name=normalized_name,
    )