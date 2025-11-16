import typer
import keyring
from keyrings.cryptfile.cryptfile import CryptFileKeyring
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from tui import FactsTUI
from conf.database import init_db
from conf.env import KEYRING_PASSWORD
from app.facts import get_fact, add_fact, add_user_fact
from app.auth import get_local_token, get_user_by_token, logout, login, signup

console = Console()

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

    # Display banner
    banner = Text()
    banner.append("███████╗ █████╗  ██████╗████████╗███████╗", style="bold cyan")
    banner.append("\n")
    banner.append("██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔════╝", style="bold cyan")
    banner.append("\n")
    banner.append("█████╗  ███████║██║        ██║   ███████╗", style="bold magenta")
    banner.append("\n")
    banner.append("██╔══╝  ██╔══██║██║        ██║   ╚════██║", style="bold magenta")
    banner.append("\n")
    banner.append("██║     ██║  ██║╚██████╗   ██║   ███████║", style="bold yellow")
    banner.append("\n")
    banner.append("╚═╝     ╚═╝  ╚═╝ ╚═════╝   ╚═╝   ╚══════╝", style="bold yellow")
    banner.append("\n\n")
    banner.append("           Interactive Shell", style="italic bright_white")

    console.print(Panel(banner, border_style="bright_blue", padding=(1, 2)))

    # Check if user is logged in
    token = get_local_token()
    user = get_user_by_token(token) if token else None

    if not user:
        console.print("\n[yellow]You need to login or signup first.[/yellow]\n")

        while not user:
            choice = typer.prompt("Choose: (l)ogin, (s)ignup, or (q)uit", default="l")

            if choice.lower() == "q":
                console.print("[cyan]Goodbye![/cyan]")
                raise typer.Exit()

            username = typer.prompt("Username")
            password = typer.prompt("Password", hide_input=True)

            if choice.lower() == "s":
                if signup(username, password):
                    console.print("[green]✓ Account created! Now logging in...[/green]")
                    token = login(username, password)
                    user = get_user_by_token(token)
                else:
                    console.print("[red]✗ Username taken. Try again.[/red]\n")
            else:
                token = login(username, password)
                user = get_user_by_token(token)
                if not user:
                    console.print("[red]✗ Login failed. Try again.[/red]\n")

    console.print(
        f"\n[green]✓ Logged in as:[/green] [bold cyan]{user.username}[/bold cyan]"
    )
    console.print(
        "\n[dim]Commands: happy, sad, random, add, history, whoami, logout, quit[/dim]"
    )
    console.print("[bright_blue]" + "=" * 60 + "[/bright_blue]\n")

    while True:
        try:
            cmd = (
                console.input("[bold magenta]facts[/bold magenta] [cyan]›[/cyan] ")
                .strip()
                .lower()
            )

            if not cmd:
                continue

            if cmd in ["quit", "exit", "q"]:
                console.print("[cyan]Goodbye![/cyan]")
                break

            elif cmd == "logout":
                token = get_local_token()
                logout(token)
                console.print("[green]✓ Logged out[/green]")
                break

            elif cmd == "whoami":
                console.print(
                    f"[cyan]Logged in as:[/cyan] [bold]{user.username}[/bold]"
                )

            elif cmd == "happy":
                fact_id, fact = get_fact(category="happy", user_id=user.id)
                if fact_id:
                    add_user_fact(user.id, fact_id)
                console.print(
                    Panel(
                        fact,
                        title="[yellow]😊 Happy Fact[/yellow]",
                        border_style="yellow",
                    )
                )

            elif cmd == "sad":
                fact_id, fact = get_fact(category="sad", user_id=user.id)
                if fact_id:
                    add_user_fact(user.id, fact_id)
                console.print(
                    Panel(fact, title="[blue]😢 Sad Fact[/blue]", border_style="blue")
                )

            elif cmd == "random":
                fact_id, fact = get_fact(category=None, user_id=user.id)
                if fact_id:
                    add_user_fact(user.id, fact_id)
                console.print(
                    Panel(
                        fact,
                        title="[magenta]🎲 Random Fact[/magenta]",
                        border_style="magenta",
                    )
                )

            elif cmd == "add":
                category = typer.prompt("Category (happy/sad)").lower()
                fact_text = typer.prompt("Fact")
                if add_fact(category, fact_text, user.id):
                    console.print("[green]✓ Fact added![/green]")
                else:
                    console.print("[red]✗ Invalid category. Use: happy or sad[/red]")

            elif cmd == "history":
                from app.facts import get_user_history

                history = get_user_history(user.id)
                if history:
                    console.print("\n[bold cyan]📜 Your History[/bold cyan]")
                    for i, h in enumerate(history[:10], 1):
                        console.print(f"[dim]{i}.[/dim] {h}")
                    console.print()
                else:
                    console.print("[yellow]No history yet.[/yellow]")

            else:
                console.print(f"[red]Unknown command:[/red] {cmd}")
                console.print(
                    "[dim]Available: happy, sad, random, add, history, whoami, logout, quit[/dim]"
                )

        except KeyboardInterrupt:
            console.print("\n\n[cyan]Goodbye![/cyan]")
            break
        except EOFError:
            console.print("\n[cyan]Goodbye![/cyan]")
            break


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
