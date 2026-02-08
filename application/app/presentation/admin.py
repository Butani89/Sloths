"""
Admin routes for managing subscribers.
Initially unprotected - authentication will be added later.
"""
from flask import Blueprint, render_template
from app.business.services.subscription_service import SubscriptionService

# Skapar en blueprint döpt till "admin".
# url_prefix="/admin" gör att alla sidor här hamnar under den adressen.
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/subscribers")
def subscribers():
    """Display list of all newsletter subscribers."""
    service = SubscriptionService()
    # Hämtar alla prenumeranter via servicelagret
    all_subscribers = service.get_all_subscribers()
    return render_template(
        "admin/subscribers.html",
        subscribers=all_subscribers,
        count=len(all_subscribers),
    )