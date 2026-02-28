import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
_root = Path(__file__).parent.parent.parent.parent
load_dotenv(_root / ".env")

API_URL = os.getenv("API_URL", "http://localhost:8000")
CLI_TOKEN_FILE = Path.home() / ".flowguard" / "token"


def get_api_url() -> str:
    return API_URL.rstrip("/")


def save_token(token: str):
    CLI_TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    CLI_TOKEN_FILE.write_text(token)


def load_token() -> str | None:
    if CLI_TOKEN_FILE.exists():
        return CLI_TOKEN_FILE.read_text().strip()
    return os.getenv("FLOWGUARD_TOKEN")
