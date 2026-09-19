import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

CFBD_API_KEY = os.environ.get("CFBD_API_KEY")
CFBD_BASE_URL = "https://api.collegefootballdata.com"

DATA_RAW_DIR = PROJECT_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def require_api_key() -> str:
    if not CFBD_API_KEY:
        raise RuntimeError(
            "CFBD_API_KEY is not set. Copy .env.example to .env and add your key "
            "from https://collegefootballdata.com/key"
        )
    return CFBD_API_KEY
