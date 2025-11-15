from textual.screen import Screen
from textual.widgets import Button, Input, Static
from textual.containers import Vertical

from app.facts import add_fact


class AddFactScreen(Screen):
    def compose(self):
        yield Vertical(
            Static("Add a Fact", id="title"),
            Static("Category (happy / sad)", id="hint"),
            Input(id="category", placeholder="e.g. happy"),
            Input(id="fact", placeholder="Type your fact here..."),
            Button("Add Fact", id="add_btn"),
            Button("Back", id="back_btn"),
            Static("", id="message"),
        )

    def on_button_pressed(self, event):
        btn_id = event.button.id
        if btn_id == "back_btn":
            self.app.pop_screen()
            return

        if btn_id == "add_btn":
            category = self.query_one("#category").value.strip().lower()
            fact = self.query_one("#fact").value.strip()

            if not category or not fact:
                self.query_one("#message", Static).update(
                    "Both category and fact are required."
                )
                self.app.bell()
                return

            success = add_fact(category, fact, self.app.user_id)
            if success:
                self.query_one("#message", Static).update("Fact added! ✅")
                self.query_one("#category", Input).value = ""
                self.query_one("#fact", Input).value = ""
            else:
                self.query_one("#message", Static).update(
                    "Invalid category. Use: happy, sad, fun"
                )
                self.app.bell()
