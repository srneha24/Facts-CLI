from textual.screen import Screen
from textual.widgets import Button, Static
from textual.containers import VerticalScroll

from app.auth import get_local_token, logout
from screens.show_fact import ShowFactScreen


class MenuScreen(Screen):

    def compose(self):
        username = getattr(self.app, "username", "Guest")
        yield VerticalScroll(
            Static(f"Hello, {username} — Choose an option", id="title"),
            Button("Happy Fact", id="happy"),
            Button("Sad Fact", id="sad"),
            Button("Random Fact", id="random"),
            Button("Add Fact", id="add"),
            Button("History", id="history"),
            Button("Logout", id="logout"),
            Static("", id="message"),
        )

    def on_button_pressed(self, event):
        btn = event.button.id

        # Logout
        if btn == "logout":
            token = get_local_token()
            logout(token)
            self.app.username = None
            self.app.pop_screen()
            self.app.push_screen("login")
            return

        # Add fact
        if btn == "add":
            self.app.push_screen("add_fact")
            return

        self.app.current_category = btn
        self.app.push_screen(ShowFactScreen())
