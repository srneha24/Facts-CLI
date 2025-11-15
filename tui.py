from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from db import init_db
from session_store import restore_session
from screens.login import LoginScreen
from screens.signup import SignupScreen
from screens.menu import MenuScreen
from screens.add_fact import AddFactScreen
from screens.show_fact import ShowFactScreen

class FactsTUI(App):
    CSS_PATH = "styles.tcss"
    TITLE = "FactsCLI TUI"
    SCREENS = {
        "login": LoginScreen,
        "signup": SignupScreen,
        "menu": MenuScreen,
        "add_fact": AddFactScreen,
        "show_fact": ShowFactScreen,
    }

    def on_mount(self):
        init_db()
        session = restore_session()
        if session:
            self.username = session["username"]
            self.push_screen("menu")
        else:
            self.push_screen("login")

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
