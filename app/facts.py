import random
from typing import List, Tuple

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


def get_facts_by_category(category: str, user_id: int) -> List[Tuple[int, str]]:
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
                db.query(UserFact.fact_id)
                .filter(UserFact.user_id == user_id)
                .all()
            )
            seen_fact_ids = {f.fact_id for f in seen_facts}

        # Filter out already seen facts
        unseen_facts = [f for f in all_facts if f.id not in seen_fact_ids]

        return [(r.id, r.fact) for r in unseen_facts]
    finally:
        db.close()


def get_fact(category: str | None, user_id: int) -> Tuple[id, str]:
    if not category:
        category = random.choice(VALID_CATEGORIES)
    rows = get_facts_by_category(category, user_id)
    if not rows:
        return None, f"No {category} facts yet."
    return random.choice(rows)


def add_user_fact(user_id: int, fact_id: int):
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
