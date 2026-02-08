"""Admin routes for managing subscribers.
Protected by @login_required - requires admin authentication.
"""
from datetime import datetime
import csv
import io
from flask import Blueprint, render_template, Response
from flask_login import login_required
from app.business.services.subscription_service import SubscriptionService

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/subscribers")
@login_required
def subscribers():
    """Display list of all newsletter subscribers."""
    service = SubscriptionService()
    all_subscribers = service.get_all_subscribers()
    return render_template(
        "admin/subscribers.html",
        subscribers=all_subscribers,
        count=len(all_subscribers),
    )

@admin_bp.route("/export/csv")
@login_required
def export_csv():
    """Export all subscribers as a downloadable CSV file."""
    service = SubscriptionService()
    all_subscribers = service.get_all_subscribers()
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(["Email", "Name", "Subscribed At"])
    
    # Write data rows
    for sub in all_subscribers:
        writer.writerow([
            sub.email,
            sub.name,
            sub.subscribed_at.strftime("%Y-%m-%d %H:%M:%S") if sub.subscribed_at else "",
        ])
    
    # Prepare response
    output.seek(0)
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"subscribers-{date_str}.csv"
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )