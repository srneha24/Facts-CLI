from textual.screen import Screen
from textual.widgets import Button, Static
from textual.containers import Vertical, VerticalScroll
from facts import get_fact
import asyncio

class ShowFactScreen(Screen):
    def compose(self):
        # A scrollable region for facts/history and buttons
        yield Vertical(
            VerticalScroll(Static("", id="fact_text"), id="scroll"),
            Button("Another", id="another_btn"),
            Button("Back", id="back_btn"),
        )

    async def on_mount(self):
        # small "loading" animation before showing fact
        self.query_one("#fact_text", Static).update("Loading...")
        await asyncio.sleep(0.25)
        category = getattr(self.app, "current_category", None)
        if not category:
            self.query_one("#fact_text", Static).update("No category selected.")
            return

        if category == "history":
            # use app.history (list of strings)
            hist = getattr(self.app, "history", [])
            text = "\n\n".join(hist) if hist else "(no history)"
            self.query_one("#fact_text", Static).update(text)
            # ensure scroll at top
            self.query_one("#scroll").scroll_home(animate=False)
            return

        fact = get_fact(category)
        display = f"[{category.upper()}]\n\n{fact}"
        self.query_one("#fact_text", Static).update(display)
        self.query_one("#scroll").scroll_home(animate=False)

    async def on_button_pressed(self, event):
        btn = event.button.id
        if btn == "back_btn":
            self.app.pop_screen()
            return

        if btn == "another_btn":
            # simple loading micro-animation
            widget = self.query_one("#fact_text", Static)
            widget.update("Loading another...")
            await asyncio.sleep(0.2)
            category = getattr(self.app, "current_category", None)
            if not category:
                widget.update("No category selected.")
                return
            fact = get_fact(category)
            widget.update(f"[{category.upper()}]\n\n{fact}")
            self.query_one("#scroll").scroll_home(animate=False)
