import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Local SQLite database path
DEFAULT_DATABASE_PATH = PROJECT_ROOT / "backend" / "surya_setu.db"

# Database connection URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"
)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg://",
        1
    )

elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )
# Application environment
APP_ENV = os.getenv("APP_ENV", "development")

# Application settings
GENERATION_PER_KW = 1400
DEFAULT_SCORE_THRESHOLD = 1000

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-secret")
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24