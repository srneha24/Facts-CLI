import uuid
import keyring
from passlib.context import CryptContext  # Keep this import

from db import SessionLocal
from models import User, SessionToken

pwd_context = CryptContext(
    schemes=["argon2"],
    default="argon2",
    # Argon2 parameters (recommended defaults):
    argon2__time_cost=2,
    argon2__memory_cost=102400,  # In kilobytes (100MB)
    argon2__parallelism=8,
)

SERVICE_NAME = "factcli"  # keyring service name


def signup(username: str, password: str) -> bool:
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            return False

        # Hashing logic remains the same, but now uses the Argon2 scheme
        hashed = pwd_context.hash(password)

        user = User(username=username, password_hash=hashed)
        db.add(user)
        db.commit()
        return True
    finally:
        db.close()


def login(username: str, password: str) -> str | None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None

        # Verification logic remains the same, using the Argon2 scheme
        if not pwd_context.verify(password, user.password_hash):
            return None

        token = str(uuid.uuid4())
        session = SessionToken(token=token, user_id=user.id)
        db.add(session)
        db.commit()
        keyring.set_password(SERVICE_NAME, "session_token", token)
        return token
    finally:
        db.close()


def logout(token: str | None):
    db = SessionLocal()
    try:
        if token:
            db.query(SessionToken).filter(SessionToken.token == token).delete()
            db.commit()
        try:
            keyring.delete_password(SERVICE_NAME, "session_token")
        except keyring.errors.PasswordDeleteError:
            pass
    finally:
        db.close()


def get_user_by_token(token: str | None):
    if not token:
        return None
    db = SessionLocal()
    try:
        s = db.query(SessionToken).filter(SessionToken.token == token).first()
        if not s:
            return None
        user = db.query(User).get(s.user_id)
        return user
    finally:
        db.close()


def get_local_token():
    try:
        return keyring.get_password(SERVICE_NAME, "session_token")
    except Exception:
        return None
