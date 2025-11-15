import typer
import keyring
from keyrings.cryptfile.cryptfile import CryptFileKeyring

from tui import FactsTUI
from conf.database import init_db
from conf.env import KEYRING_PASSWORD
from app.facts import get_fact, add_fact, add_user_fact
from app.auth import get_local_token, get_user_by_token, logout

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
            "Use `factscli ui` for the TUI or run subcommands. Use --help for options."
        )
        raise typer.Exit()


@app.command()
def ui():
    """Starts the Text User Interface (TUI)."""
    # The TUI should now only handle user login, not keyring initialization.
    FactsTUI().run()


@app.command()
def happy():
    """Gets a random 'happy' fact."""
    token = get_local_token()
    if not token:
        typer.echo("Not logged in. Please use the TUI to login first.")
        raise typer.Exit()
    user = get_user_by_token(token)
    if not user:
        typer.echo("Session invalid. Please login again.")
        raise typer.Exit()

    fact_id, fact = get_fact(category="happy", user_id=user.id)
    if fact_id:
        add_user_fact(user.id, fact_id)
    typer.echo(fact)


@app.command()
def sad():
    """Gets a random 'sad' fact."""
    token = get_local_token()
    if not token:
        typer.echo("Not logged in. Please use the TUI to login first.")
        raise typer.Exit()
    user = get_user_by_token(token)
    if not user:
        typer.echo("Session invalid. Please login again.")
        raise typer.Exit()

    fact_id, fact = get_fact(category="sad", user_id=user.id)
    if fact_id:
        add_user_fact(user.id, fact_id)
    typer.echo(fact)


@app.command()
def random():
    """Gets a random fact from any category."""
    token = get_local_token()
    if not token:
        typer.echo("Not logged in. Please use the TUI to login first.")
        raise typer.Exit()
    user = get_user_by_token(token)
    if not user:
        typer.echo("Session invalid. Please login again.")
        raise typer.Exit()

    fact_id, fact = get_fact(category=None, user_id=user.id)
    if fact_id:
        add_user_fact(user.id, fact_id)
    typer.echo(fact)


@app.command()
def add(category: str, fact: str):
    """Adds a new fact to a specified category."""
    token = get_local_token()
    if not token:
        typer.echo("Not logged in. Please use the TUI to login first.")
        raise typer.Exit()
    user = get_user_by_token(token)
    if not user:
        typer.echo("Session invalid. Please login again.")
        raise typer.Exit()

    ok = add_fact(category, fact, user.id)
    typer.echo("Fact added!" if ok else "Invalid category. Use: happy, sad")


@app.command()
def whoami():
    """Displays the currently logged-in user."""
    token = get_local_token()
    if not token:
        typer.echo("Not logged in")
        raise typer.Exit()
    user = get_user_by_token(token)
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
