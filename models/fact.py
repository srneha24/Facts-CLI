from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from conf.database import Base


class Fact(Base):
    __tablename__ = "facts"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True, nullable=False)
    fact = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)
    is_created_by_llm = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    added_by = relationship("User", back_populates="created_facts")
    user_facts = relationship("UserFact", back_populates="fact")
