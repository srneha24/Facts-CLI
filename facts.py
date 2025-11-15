from db import SessionLocal
from models import Fact
import random
from typing import List

VALID_CATEGORIES = ["happy", "sad", "fun"]

def add_fact(category: str, fact_text: str) -> bool:
    category = category.lower()
    if category not in VALID_CATEGORIES:
        return False
    db = SessionLocal()
    try:
        f = Fact(category=category, fact=fact_text)
        db.add(f)
        db.commit()
        return True
    finally:
        db.close()

def get_facts_by_category(category: str) -> List[str]:
    db = SessionLocal()
    try:
        rows = db.query(Fact).filter(Fact.category == category).all()
        return [r.fact for r in rows]
    finally:
        db.close()

def get_fact(category: str) -> str:
    rows = get_facts_by_category(category)
    if not rows:
        return f"No {category} facts yet."
    return random.choice(rows)
