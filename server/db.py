from __future__ import annotations

import os
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DATABASE_URL")


def _get_database_url() -> str:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is required for Supabase Postgres.")
    return DATABASE_URL


def get_connection() -> Any:
    db_url = _get_database_url()
    connect_kwargs: dict[str, Any] = {}
    if "sslmode=" not in db_url:
        connect_kwargs["sslmode"] = os.getenv("PG_SSLMODE", "require")
    return psycopg2.connect(db_url, cursor_factory=RealDictCursor, **connect_kwargs)


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tokens (
            token TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_used_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS notices (
            id TEXT PRIMARY KEY,
            vtuber_id TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )
    conn.commit()
    conn.close()
