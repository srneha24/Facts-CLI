from textual.screen import Screen
from textual.widgets import Button, Static
from textual.containers import VerticalScroll
from auth import get_local_token, logout
from facts import get_facts_by_category


class MenuScreen(Screen):

    def compose(self):
        username = getattr(self.app, "username", "Guest")
        yield VerticalScroll(
            Static(f"Hello, {username} — Choose an option", id="title"),
            Button("Happy Fact", id="happy"),
            Button("Sad Fact", id="sad"),
            Button("Fun Fact", id="fun"),
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

        # History
        if btn == "history":
            hist = []
            for cat in ["happy", "sad", "fun"]:
                rows = get_facts_by_category(cat)
                hist.append(f"--- {cat.upper()} ---")
                hist.extend(rows or ["(no facts)"])

            self.app.current_category = "history"
            self.app.history = hist
            self.app.push_screen("show_fact")
            return

        # Single fact category
        self.app.current_category = btn
        self.app.push_screen("show_fact")
