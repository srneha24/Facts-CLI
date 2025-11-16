import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from app.facts import add_fact, get_user_history
from app.fact_handler import retrieve_fact
from app.auth import get_local_token, get_user_by_token, logout, login, signup


def get_user():
    token = get_local_token()
    if not token:
        typer.echo("Not logged in. Please use the TUI to login first.")
        raise typer.Exit()
    user = get_user_by_token(token)
    if not user:
        typer.echo("Session invalid. Please login again.")
        raise typer.Exit()
    return user


def get_fact(category: str) -> str:
    user = get_user()
    if category == "random":
        category = None
    return retrieve_fact(category, user.id, show_animation=True)


def add_fact_from_user(category: str, fact: str):
    user = get_user()
    return add_fact(category, fact, user.id)


def retrieve_history() -> str:
    user = get_user()
    history = get_user_history(user_id=user.id)
    return "\n".join([f"- {hist}" for hist in history]) if history else "No history yet"


def interactive_shell():
    console = Console()

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
                fact = retrieve_fact(
                    category="happy", user_id=user.id, show_animation=True
                )
                console.print(
                    Panel(
                        fact,
                        title="[yellow]😊 Happy Fact[/yellow]",
                        border_style="yellow",
                    )
                )

            elif cmd == "sad":
                fact = retrieve_fact(
                    category="sad", user_id=user.id, show_animation=True
                )
                console.print(
                    Panel(fact, title="[blue]😢 Sad Fact[/blue]", border_style="blue")
                )

            elif cmd == "random":
                fact = retrieve_fact(
                    category=None, user_id=user.id, show_animation=True
                )
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
