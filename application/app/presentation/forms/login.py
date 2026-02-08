"""Login form for admin authentication."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    """Admin login form.
    Uses WTForms validators for server-side validation
    and Flask-WTF for automatic CSRF protection.
    """
    username = StringField("Username", validators=[
        DataRequired(message="Username is required")
    ])
    password = PasswordField("Password", validators=[
        DataRequired(message="Password is required")
    ])
    submit = SubmitField("Log In")