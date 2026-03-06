"""
database.py — SQLAlchemy engine & session factory
==================================================
Reads connection details from environment variables so credentials are never
hard-coded.  Defaults are provided for local development only.

Usage (from other modules):
    from sqlalchemy.database import engine, session
"""

import os
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# ── Connection parameters ─────────────────────────────────────────────────────
# Always set POSTGRES_PASSWORD via an environment variable in production —
# never commit passwords to source control.
user = os.getenv("POSTGRES_USER", "postgres")
pw   = quote_plus(os.getenv("POSTGRES_PASSWORD", "root"))  # encodes special chars
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")
db   = os.getenv("POSTGRES_DB", "Product")

DATABASE_URL = f"postgresql://{user}:{pw}@{host}:{port}/{db}"

# ── Engine ────────────────────────────────────────────────────────────────────
# create_engine() builds the connection-pool / gateway to the database.
engine = create_engine(DATABASE_URL)

# ── Session factory ───────────────────────────────────────────────────────────
# autocommit=False  → we control when writes are committed (safer).
# autoflush=False   → we control when pending changes are flushed to the DB.
# bind=engine       → every session talks to our PostgreSQL instance.
session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
