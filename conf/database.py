from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from conf.env import DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db():
    # Import models to register them before creating tables
    from models import User, Fact, SessionToken  # noqa: F401

    Base.metadata.create_all(bind=engine)
