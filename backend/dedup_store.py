"""
FireReach — Deduplication Store (SQLite)
Prevents sending to same company twice within 90 days.
Key: sha256(company_domain + smtp_user)
"""

import os
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = os.getenv("DEDUP_DB_PATH", "data/dedup.db")

def _get_conn():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    # Enable WAL mode for concurrent access
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sent_log (
            dedup_key   TEXT PRIMARY KEY,
            domain      TEXT,
            sender      TEXT,
            sent_at     TEXT,
            signal_ids  TEXT    -- comma-separated signal IDs used
        )
    """)
    conn.commit()
    return conn

def _key(domain: str, sender: str) -> str:
    return hashlib.sha256(f"{domain.lower()}:{sender.lower()}".encode()).hexdigest()[:16]

def already_sent(domain: str, sender: str, days: int = 90) -> bool:
    """Returns True if this domain was already contacted within `days` days."""
    conn = _get_conn()
    try:
        key    = _key(domain, sender)
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        row    = conn.execute(
            "SELECT sent_at FROM sent_log WHERE dedup_key=? AND sent_at>?",
            (key, cutoff)
        ).fetchone()
        return row is not None
    finally:
        conn.close()

def record_sent(domain: str, sender: str, signal_ids: list[str]):
    """Record that this domain was contacted now."""
    conn = _get_conn()
    try:
        key = _key(domain, sender)
        conn.execute(
            "INSERT OR REPLACE INTO sent_log (dedup_key, domain, sender, sent_at, signal_ids) VALUES (?,?,?,?,?)",
            (key, domain, sender, datetime.utcnow().isoformat(), ",".join(signal_ids))
        )
        conn.commit()
    finally:
        conn.close()

def get_used_signals(domain: str, sender: str) -> list[str]:
    """Return signal_ids used in previous sends to this domain."""
    conn = _get_conn()
    try:
        key = _key(domain, sender)
        row = conn.execute(
            "SELECT signal_ids FROM sent_log WHERE dedup_key=?", (key,)
        ).fetchone()
        if row and row[0]:
            return row[0].split(",")
        return []
    finally:
        conn.close()