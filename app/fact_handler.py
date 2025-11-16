import random
from langchain_core.messages import HumanMessage
from typing import Literal

from app.facts import get_user_history
from app.agent import create_agent_state_graph


def retrieve_fact(category: Literal["happy", "sad"] | None, user_id: int) -> str:
    fact_sources = ["llm", "db"]
    fact_source = random.choices(
        fact_sources, weights=[0.3, 0.7], k=1
    )[0]
    if not category:
        category = random.choice(["happy", "sad"])
    
    if fact_source == "db":
        user_message = HumanMessage(content=f"Tell me a {category} fact from the database.")
    else:
        user_message = HumanMessage(content=f"Generate a {category} fact yourself.")
    
    user_history = get_user_history(user_id=user_id)
    shown_facts = "\n".join([f"- {shown_fact}" for shown_fact in user_history])

    agent = create_agent_state_graph(known_facts=shown_facts, user_id=user_id)
