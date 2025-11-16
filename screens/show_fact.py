import asyncio
from textual.screen import Screen
from textual.widgets import Button, Static
from textual.containers import Vertical, VerticalScroll

from app.facts import get_user_history
from app.fact_handler import retrieve_fact


class ShowFactScreen(Screen):

    def compose(self):
        yield Vertical(
            VerticalScroll(Static("", id="fact_text"), id="scroll"),
            Button("Another", id="another_btn", classes="another-btn"),
            Button("Back", id="back_btn"),
        )

    def on_mount(self):
        widget = self.query_one("#fact_text", Static)
        widget.update("Loading...")

        self.call_after_refresh(self.load_fact)

    async def load_fact(self):
        await asyncio.sleep(0.2)

        category = getattr(self.app, "current_category", None)
        widget = self.query_one("#fact_text", Static)
        scroll = self.query_one("#scroll")
        another_btn = self.query_one("#another_btn", Button)

        if not category:
            widget.update("No category selected.")
            return

        if category == "history":
            # Hide the "Another" button when viewing history
            another_btn.display = False
            history = get_user_history(self.app.user_id)
            widget.update("\n\n".join(history) if history else "(no history)")
            scroll.scroll_home(animate=False)
            return

        # Show the "Another" button for regular fact viewing
        another_btn.display = True

        fact_category = category
        if category == "random":
            fact_category = None
        
        fact = retrieve_fact(category=fact_category, user_id=self.app.user_id)

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

            fact_category = category
            if category == "random":
                fact_category = None

            fact = retrieve_fact(category=fact_category, user_id=self.app.user_id)

            widget.update(f"[{category.upper()}]\n\n{fact}")
            self.query_one("#scroll").scroll_home(animate=False)
