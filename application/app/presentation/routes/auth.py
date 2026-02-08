"""Authentication routes for login and logout.
Uses Flask-Login for session management and AuthService
for credential verification.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.business.services.auth_service import AuthService
from app.presentation.forms.login import LoginForm

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Display and handle the login form."""
    # Already logged in? Redirect to admin
    if current_user.is_authenticated:
        return redirect(url_for("admin.subscribers"))

    form = LoginForm()
    if form.validate_on_submit():
        user = AuthService.authenticate(form.username.data, form.password.data)
        if user:
            login_user(user)
            flash("Login successful!", "success")
            
            # Redirect to originally requested page or admin
            next_page = request.args.get("next")
            if next_page and next_page.startswith("/"):
                return redirect(next_page)
            
            return redirect(url_for("admin.subscribers"))
        else:
            flash("Invalid username or password.", "error")
    
    return render_template("auth/login.html", form=form)

@auth_bp.route("/logout")
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("public.index"))