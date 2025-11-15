from sqlalchemy import Column, Integer, String, Text
from db import Base


class Fact(Base):
    __tablename__ = "facts"
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True, nullable=False)
    fact = Column(Text, nullable=False)
