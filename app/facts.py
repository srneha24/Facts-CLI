import random
from typing import List, Tuple, Literal

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


def add_llm_fact(category: Literal["happy", "sad"], fact_text: str) -> int | None:
    """Add a fact created by the LLM to the database.
    Args:
        category (Literal["happy", "sad"]): The category of the fact
        fact_text (str): The text of the fact
    Returns:
        int | None: The ID of the newly created fact, or None if the category is invalid
    """
    category = category.lower()
    if category not in VALID_CATEGORIES:
        return None
    db = SessionLocal()
    try:
        fact = Fact(
            category=category, fact=fact_text, user_id=None, is_created_by_llm=True
        )
        db.add(fact)
        db.commit()
        return fact.id
    finally:
        db.close()


def get_fact_from_db(
    category: Literal["happy", "sad"], user_id: int
) -> Tuple[id, str]:
    """Retrieve a fact from the database by category (happy, sad), excluding those created by the user.

    Args:
        category (Literal["happy", "sad"]): The category of fact to retrieve
        user_id (int): The ID of the user requesting the fact
    Returns:
        Tuple[id, str]: A tuple containing the fact ID and the fact text
    """
    db = SessionLocal()
    try:
        # Exclude facts created by the user
        query = db.query(Fact).filter(Fact.category == category)
        if user_id is not None:
            query = query.filter(Fact.user_id != user_id)

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

        rows = [(r.id, r.fact) for r in unseen_facts]

        if not rows:
            return None, f"No {category} facts yet."
        return random.choice(rows)
    finally:
        db.close()


def add_user_fact(user_id: int, fact_id: int):
    """Record that a user has seen a fact.
    Args:
        user_id (int): The ID of the user
        fact_id (int): The ID of the fact
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
