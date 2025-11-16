import random
from typing import List, Literal

from conf.database import SessionLocal
from models import Fact, UserFact

VALID_CATEGORIES = ["happy", "sad"]


def add_fact(category: str, fact_text: str, user_id: int) -> bool:
    category = category.lower()
    if category not in VALID_CATEGORIES:
        return False
    db = SessionLocal()
    try:
        f = Fact(
            category=category, fact=fact_text, user_id=user_id, is_created_by_llm=False
        )
        db.add(f)
        db.commit()
        return True
    finally:
        db.close()


def add_llm_fact(category: Literal["happy", "sad"], fact_text: str, user_id: int | str) -> dict:
    """Add a fact created by the LLM to the database.

    Args:
        category: The category of the fact
        fact_text: The text of the fact
        user_id: The ID of the user requesting the fact (required for tool binding, can be string or int)

    Returns:
        A dictionary with fact_id and fact_text keys
    """
    # Convert user_id to int if it's a string (LLM sometimes passes it as string)
    if isinstance(user_id, str):
        user_id = int(user_id)

    category = category.lower()
    if category not in VALID_CATEGORIES:
        return {"fact_id": -1, "fact_text": f"Invalid category: {category}"}
    db = SessionLocal()
    try:
        fact = Fact(
            category=category, fact=fact_text, user_id=None, is_created_by_llm=True
        )
        db.add(fact)
        db.commit()
        db.refresh(fact)
        return {"fact_id": fact.id, "fact_text": fact.fact}
    finally:
        db.close()


def get_fact_from_db(
    category: Literal["happy", "sad"], user_id: int | str
) -> dict:
    """Retrieve a fact from the database by category (happy, sad), excluding those created by the user.

    Args:
        category: The category of fact to retrieve
        user_id: The ID of the user requesting the fact (can be string or int)

    Returns:
        A dictionary with fact_id and fact_text keys
    """
    # Convert user_id to int if it's a string (LLM sometimes passes it as string)
    if isinstance(user_id, str):
        user_id = int(user_id)

    db = SessionLocal()
    try:
        # Exclude facts created by the user
        query = db.query(Fact).filter(Fact.category == category)
        if user_id is not None:
            # Exclude facts created by this user, but include LLM-generated facts (user_id is None)
            query = query.filter((Fact.user_id != user_id) | (Fact.user_id == None))

        # Get all facts that match the category
        all_facts = query.all()

        # Get IDs of facts the user has already seen
        seen_fact_ids = set()
        if user_id is not None:
            seen_facts = (
                db.query(UserFact.fact_id).filter(UserFact.user_id == user_id).all()
            )
            seen_fact_ids = {f.fact_id for f in seen_facts}

        # Filter out already seen facts
        unseen_facts = [f for f in all_facts if f.id not in seen_fact_ids]

        if not unseen_facts:
            return {"fact_id": -1, "fact_text": f"No {category} facts yet."}

        chosen_fact = random.choice(unseen_facts)
        return {"fact_id": chosen_fact.id, "fact_text": chosen_fact.fact}
    finally:
        db.close()


def add_user_fact(user_id: int, fact_id: int) -> None:
    """Record that a user has seen a fact.

    Args:
        user_id: The ID of the user
        fact_id: The ID of the fact
    """
    db = SessionLocal()
    try:
        uf = UserFact(user_id=user_id, fact_id=fact_id)
        db.add(uf)
        db.commit()
    finally:
        db.close()


def get_user_history(user_id: int) -> List[str]:
    db = SessionLocal()
    try:
        rows = (
            db.query(Fact.fact)
            .join(UserFact, Fact.id == UserFact.fact_id)
            .filter(UserFact.user_id == user_id)
            .order_by(UserFact.created_at.desc())
            .all()
        )
        return [r.fact for r in rows]
    finally:
        db.close()
