import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Fallback SQLite for local dev
DEFAULT_SQLITE = f"sqlite:///{Path('database.sqlite3').absolute()}"
DATABASE_URL = os.environ.get("FACTCLI_DATABASE_URL", DEFAULT_SQLITE)

KEYRING_PASSWORD = os.environ.get("KEYRING_PASSWORD")

LLM = os.environ.get("LLM")
