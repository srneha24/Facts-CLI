import typer
import keyring
from typer import Option
from keyrings.cryptfile.cryptfile import CryptFileKeyring

from tui import FactsTUI
from conf.database import init_db
from conf.env import KEYRING_PASSWORD
from app.auth import get_local_token, logout, signup
from app.cli import (
    get_fact,
    get_user,
    add_fact_from_user,
    interactive_shell,
    retrieve_history,
)

app_keyring = CryptFileKeyring()
app_keyring.keyring_key = KEYRING_PASSWORD
keyring.set_keyring(app_keyring)

_ = get_local_token()

app = typer.Typer(help="FactsCLI")


@app.callback(invoke_without_command=True)
def startup(ctx: typer.Context):
    """Initializes the database and checks for TUI command."""
    init_db()
    if ctx.invoked_subcommand is None:
        typer.echo(
            "Use `factscli ui` for the TUI, `factscli shell` for interactive CLI, or run subcommands. Use --help for options."
        )
        raise typer.Exit()


@app.command()
def ui():
    """Starts the Text User Interface (TUI)."""
    FactsTUI().run()


@app.command()
def shell():
    """Starts an interactive CLI shell session."""
    init_db()
    interactive_shell()


@app.command()
def signup(
    username: str = Option(..., "--category", "-c", help="Fact category"),
    password: str = Option(..., "--fact", "-f", help="Fact text"),
):
    """Signs up the user."""
    if signup(username, password):
        typer.echo("Signup successful! You can now login.")
    else:
        typer.echo("Username taken. Try another.")


@app.command()
def happy():
    """Gets a random 'happy' fact."""
    fact = get_fact(category="happy")
    typer.echo(fact)


@app.command()
def sad():
    """Gets a random 'sad' fact."""
    fact = get_fact(category="sad")
    typer.echo(fact)


@app.command()
def random():
    """Gets a random fact from any category."""
    fact = get_fact(category="random")
    typer.echo(fact)


@app.command()
def history():
    """Get user's history"""
    history = retrieve_history()
    typer.echo(history)


@app.command()
def add(
    category: str = Option(..., "--category", "-c", help="Fact category"),
    fact: str = Option(..., "--fact", "-f", help="Fact text"),
):
    """Adds a new fact to a specified category."""
    ok = add_fact_from_user(category, fact)
    typer.echo("Fact added!" if ok else "Invalid category. Use: happy, sad")


@app.command()
def whoami():
    """Displays the currently logged-in user."""
    user = get_user()
    if not user:
        typer.echo("Session invalid")
    else:
        typer.echo(f"Logged in as: {user.username}")


@app.command()
def signout():
    """Signs out the current user by deleting the session token."""
    token = get_local_token()
    logout(token)
    typer.echo("Signed out (if there was a session).")


if __name__ == "__main__":
    app()
