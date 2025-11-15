from textual.screen import Screen
from textual.widgets import Button, Input, Static
from textual.containers import Vertical
from auth import signup

class SignupScreen(Screen):
    def compose(self):
        yield Vertical(
            Static("Create an Account", id="title"),
            Input(placeholder="Username", id="username"),
            Input(placeholder="Password", password=True, id="password"),
            Button("Create Account", id="create_btn"),
            Button("Back to Login", id="back_btn"),
            Static("", id="message"),
        )

    def on_button_pressed(self, event):
        if event.button.id == "back_btn":
            self.app.pop_screen()
            return

        if event.button.id == "create_btn":
            username = self.query_one("#username").value.strip()
            password = self.query_one("#password").value.strip()
            if not username or not password:
                self.query_one("#message", Static).update("Both fields are required.")
                self.app.bell()
                return

            ok = signup(username, password)
            if ok:
                self.query_one("#message", Static).update("Account created! You can now log in.")
            else:
                self.query_one("#message", Static).update("Username taken. Try another.")
                self.app.bell()
