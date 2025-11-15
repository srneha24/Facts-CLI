import asyncio
from textual.screen import Screen
from textual.widgets import Button, Static
from textual.containers import Vertical, VerticalScroll

from facts import get_fact


class ShowFactScreen(Screen):

    def compose(self):
        yield Vertical(
            VerticalScroll(Static("", id="fact_text"), id="scroll"),
            Button("Another", id="another_btn"),
            Button("Back", id="back_btn"),
        )

    def on_show(self):
        widget = self.query_one("#fact_text", Static)
        widget.update("Loading...")

        self.call_after_refresh(self.load_fact)

    async def load_fact(self):
        await asyncio.sleep(0.2)

        category = getattr(self.app, "current_category", None)
        widget = self.query_one("#fact_text", Static)
        scroll = self.query_one("#scroll")

        if not category:
            widget.update("No category selected.")
            return

        if category == "history":
            hist = getattr(self.app, "history", [])
            widget.update("\n\n".join(hist) if hist else "(no history)")
            scroll.scroll_home(animate=False)
            return

        fact = get_fact(category)

        widget.update(f"[{category.upper()}]\n\n{fact}")
        scroll.scroll_home(animate=False)

    async def on_button_pressed(self, event):
        btn = event.button.id

        if btn == "back_btn":
            self.app.pop_screen()
            return

        if btn == "another_btn":
            widget = self.query_one("#fact_text", Static)
            widget.update("Loading another...")
            await asyncio.sleep(0.15)

            category = getattr(self.app, "current_category")

            fact = get_fact(category)

            widget.update(f"[{category.upper()}]\n\n{fact}")
            self.query_one("#scroll").scroll_home(animate=False)
