from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from conf.database import Base


class UserFact(Base):
    __tablename__ = "user_facts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    fact_id = Column(Integer, ForeignKey("facts.id"), index=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "fact_id", name="uix_user_fact"),)

    user = relationship("User", back_populates="user_facts")
    fact = relationship("Fact", back_populates="user_facts")
