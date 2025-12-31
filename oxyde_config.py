"""Oxyde ORM configuration."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODELS = ["models"]
DIALECT = "sqlite"
MIGRATIONS_DIR = "migrations"
DATABASES = {
    "default": f"sqlite:///{BASE_DIR}/blog.db",
}
