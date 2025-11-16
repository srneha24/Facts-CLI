import random
import threading
import time
import sys
from langchain_core.messages import HumanMessage
from typing import Literal

from app.facts import get_user_history, add_user_fact
from app.agent import create_agent_state_graph
from app.schema import Fact


class LoadingAnimation:
    """Context manager for displaying an animated loading message."""

    def __init__(self, message: str = "Loading some facts for you"):
        self.message = message
        self.is_running = False
        self.thread = None

    def _animate(self):
        """Animation loop that adds/removes ellipses."""
        ellipses = ["", ".", "..", "..."]
        idx = 0
        while self.is_running:
            # Clear the line and print message with current ellipses
            sys.stdout.write(f"\r{self.message}{ellipses[idx]}")
            sys.stdout.flush()
            idx = (idx + 1) % len(ellipses)
            time.sleep(0.5)
        # Clear the line when done
        sys.stdout.write("\r" + " " * (len(self.message) + 3) + "\r")
        sys.stdout.flush()

    def __enter__(self):
        """Start the animation."""
        self.is_running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        """Stop the animation."""
        self.is_running = False
        if self.thread:
            self.thread.join()


def retrieve_fact(
    category: Literal["happy", "sad"] | None, user_id: int, show_animation: bool = False
) -> str:
    fact_sources = ["llm", "db"]
    fact_source = random.choices(fact_sources, weights=[0.3, 0.7], k=1)[0]

    if not category:
        category = random.choice(["happy", "sad"])

    if fact_source == "db":
        user_message = HumanMessage(
            content=f"Tell me a {category} fact from the database."
        )
    else:
        user_message = HumanMessage(content=f"Generate a {category} fact yourself.")

    user_history = get_user_history(user_id=user_id)
    shown_facts = "\n".join([f"- {shown_fact}" for shown_fact in user_history])

    agent = create_agent_state_graph(known_facts=shown_facts, user_id=user_id)

    # Show loading animation while invoking the agent (only for CLI)
    if show_animation:
        with LoadingAnimation("Loading some facts for you"):
            result = agent.invoke({"messages": [user_message]})
    else:
        result = agent.invoke({"messages": [user_message]})

    # Extract the final message from the agent
    final_message = result["messages"][-1]

    # Parse the Fact response (should be JSON string from format_fact node)
    if isinstance(final_message.content, str):
        try:
            import json
            fact_data = json.loads(final_message.content)
            fact_obj = Fact(**fact_data)
        except (json.JSONDecodeError, Exception):
            # Fallback: return the raw content
            return str(final_message.content)
    elif isinstance(final_message.content, dict):
        fact_obj = Fact(**final_message.content)
    elif isinstance(final_message.content, Fact):
        fact_obj = final_message.content
    else:
        # Fallback: return the raw content
        return str(final_message.content)

    # Check if this is an error fact (fact_id = -1 means no fact was found)
    if fact_obj.fact_id == -1:
        # Don't record error facts, just return the error message
        return fact_obj.fact_text

    # Record that the user has seen this fact
    add_user_fact(user_id=user_id, fact_id=fact_obj.fact_id)

    # Return the fact text
    return fact_obj.fact_text
