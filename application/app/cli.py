"""Flask CLI commands for application management."""
import click
from flask.cli import with_appcontext
from app.business.services.auth_service import AuthService, DuplicateUsernameError

@click.command("create-admin")
@click.argument("username")
@click.option("--password", "-p", default=None,
              help="Admin password (min 8 chars). Prompted if not provided.")
@with_appcontext
def create_admin_command(username, password):
    """Create a new admin user.
    USERNAME: The username for the new admin account.
    """
    # Prompt for password if not provided
    if password is None:
        password = click.prompt("Password", hide_input=True,
                                confirmation_prompt=True)

    # Validate password length
    if len(password) < 8:
        click.echo("Error: Password must be at least 8 characters long.",
                   err=True)
        raise SystemExit(1)

    try:
        user = AuthService.create_user(username, password)
        click.echo(f"Admin user '{user.username}' created successfully.")
    except DuplicateUsernameError:
        click.echo(f"Error: Username '{username}' already exists.", err=True)
        raise SystemExit(1)