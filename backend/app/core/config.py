"""Application configuration loaded consistently for every backend module."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(ENV_FILE, override=False)


def _required(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(f"{name} is not configured")
    return value


@dataclass(frozen=True)
class Settings:
    database_url: str
    jwt_secret_key: str


settings = Settings(
    database_url=_required("DATABASE_URL"),
    jwt_secret_key=_required("JWT_SECRET_KEY"),
)
