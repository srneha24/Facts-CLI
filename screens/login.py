# screens/login.py
from textual.screen import Screen
from textual.widgets import Button, Input, Static
from textual.containers import Vertical

from app.auth import login, get_user_by_token

class LoginScreen(Screen):
    def compose(self):
        yield Vertical(
            Static("Welcome to FactsCLI", id="title"),
            Input(placeholder="Username", id="username"),
            Input(placeholder="Password", password=True, id="password"),
            Button("Login", id="login_btn"),
            Button("Signup", id="signup_btn"),
            Static("", id="message"),
        )

    def on_button_pressed(self, event):
        btn = event.button.id
        if btn == "signup_btn":
            self.app.push_screen("signup")
            return

        if btn == "login_btn":
            username = self.query_one("#username", Input).value
            password = self.query_one("#password", Input).value
            token = login(username, password)
            if token:
                user = get_user_by_token(token)
                self.app.username = username
                self.app.user_id = user.id if user else None
                self.app.push_screen("menu")
            else:
                self.query_one("#message", Static).update("Login failed — check credentials.")
                self.app.bell()
