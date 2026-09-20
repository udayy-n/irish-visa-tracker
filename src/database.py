import os
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg


# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "visa_tracker.db"

INDIA_TZ = ZoneInfo("Asia/Kolkata")


# --------------------------------------------------
# Database connection
# --------------------------------------------------

def using_postgres():
    """
    Returns True when DATABASE_URL is available.

    Local computer:
        SQLite

    Render:
        PostgreSQL
    """
    return bool(os.getenv("DATABASE_URL"))


def get_connection():
    """
    Create a database connection.

    If DATABASE_URL exists -> PostgreSQL
    Otherwise -> SQLite
    """

    if using_postgres():
        return psycopg.connect(os.getenv("DATABASE_URL"))

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    return sqlite3.connect(DB_PATH)


# --------------------------------------------------
# Current India time
# --------------------------------------------------

def current_time():
    """
    Return current time in India timezone.
    """
    return datetime.now(INDIA_TZ).isoformat()


def current_date():
    """
    Return current date in India timezone.
    """
    return datetime.now(INDIA_TZ).date().isoformat()


# --------------------------------------------------
# Create database tables
# --------------------------------------------------

def create_database():
    """
    Create all required tables if they don't already exist.
    """

    with get_connection() as conn:

        if using_postgres():

            conn.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    application_number TEXT PRIMARY KEY,
                    decision TEXT NOT NULL,
                    first_seen TEXT,
                    last_seen TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS decision_updates (
                    id SERIAL PRIMARY KEY,
                    detected_at TEXT NOT NULL,
                    total_new INTEGER NOT NULL,
                    approved INTEGER NOT NULL,
                    refused INTEGER NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_files (
                    id SERIAL PRIMARY KEY,
                    file_url TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_hash TEXT NOT NULL UNIQUE,
                    processed_at TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS update_days (
                    update_date TEXT PRIMARY KEY,
                    processed_at TEXT NOT NULL
                )
            """)

        else:

            conn.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    application_number TEXT PRIMARY KEY,
                    decision TEXT NOT NULL,
                    first_seen TEXT,
                    last_seen TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS decision_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detected_at TEXT NOT NULL,
                    total_new INTEGER NOT NULL,
                    approved INTEGER NOT NULL,
                    refused INTEGER NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS processed_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_url TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_hash TEXT NOT NULL UNIQUE,
                    processed_at TEXT NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS update_days (
                    update_date TEXT PRIMARY KEY,
                    processed_at TEXT NOT NULL
                )
            """)


# --------------------------------------------------
# Applications
# --------------------------------------------------

def get_existing_applications():
    """
    Return all application numbers already stored
    in the database.
    """

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT application_number
            FROM applications
        """).fetchall()

    return {row[0] for row in rows}


def get_application_decision(application_number):
    """
    Return the decision for one application number.

    Application number must contain digits only.
    """

    application_number = str(application_number).strip()

    with get_connection() as conn:

        if using_postgres():

            row = conn.execute(
                """
                SELECT decision
                FROM applications
                WHERE application_number = %s
                """,
                (application_number,)
            ).fetchone()

        else:

            row = conn.execute(
                """
                SELECT decision
                FROM applications
                WHERE application_number = ?
                """,
                (application_number,)
            ).fetchone()

    if row:
        return row[0]

    return None


def insert_applications(data, baseline=False):
    """
    Insert application decisions into the database.

    baseline=True:
        These applications already existed when
        tracking started.
        first_seen is stored as NULL.

    baseline=False:
        These are newly detected applications.
        first_seen is set to the current India time.
    """

    now = current_time()

    records = []

    for row in data.itertuples(index=False):

        application_number = str(row.application_number).strip()
        decision = str(row.decision).strip()

        if baseline:
            first_seen = None
        else:
            first_seen = now

        records.append(
            (
                application_number,
                decision,
                first_seen,
                now
            )
        )

    if not records:
        return

    with get_connection() as conn:

        # PostgreSQL
        if using_postgres():

            with conn.cursor() as cur:

                cur.executemany(
                    """
                    INSERT INTO applications
                    (
                        application_number,
                        decision,
                        first_seen,
                        last_seen
                    )
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (application_number) DO NOTHING
                    """,
                    records
                )

        # SQLite
        else:

            conn.executemany(
                """
                INSERT OR IGNORE INTO applications
                (
                    application_number,
                    decision,
                    first_seen,
                    last_seen
                )
                VALUES (?, ?, ?, ?)
                """,
                records
            )


# --------------------------------------------------
# Daily statistics
# --------------------------------------------------

def save_update_statistics(total_new, approved, refused):
    """
    Save statistics for one detected update.
    """

    with get_connection() as conn:

        if using_postgres():

            conn.execute(
                """
                INSERT INTO decision_updates
                (
                    detected_at,
                    total_new,
                    approved,
                    refused
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    current_time(),
                    total_new,
                    approved,
                    refused
                )
            )

        else:

            conn.execute(
                """
                INSERT INTO decision_updates
                (
                    detected_at,
                    total_new,
                    approved,
                    refused
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    current_time(),
                    total_new,
                    approved,
                    refused
                )
            )


# --------------------------------------------------
# Processed files / SHA-256
# --------------------------------------------------

def is_file_processed(file_hash):
    """
    Check whether an ODS file hash has already
    been processed.
    """

    with get_connection() as conn:

        if using_postgres():

            row = conn.execute(
                """
                SELECT 1
                FROM processed_files
                WHERE file_hash = %s
                """,
                (file_hash,)
            ).fetchone()

        else:

            row = conn.execute(
                """
                SELECT 1
                FROM processed_files
                WHERE file_hash = ?
                """,
                (file_hash,)
            ).fetchone()

    return row is not None


def save_processed_file(file_url, filename, file_hash):
    """
    Record an ODS file as processed.
    """

    with get_connection() as conn:

        if using_postgres():

            conn.execute(
                """
                INSERT INTO processed_files
                (
                    file_url,
                    filename,
                    file_hash,
                    processed_at
                )
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (file_hash) DO NOTHING
                """,
                (
                    file_url,
                    filename,
                    file_hash,
                    current_time()
                )
            )

        else:

            conn.execute(
                """
                INSERT OR IGNORE INTO processed_files
                (
                    file_url,
                    filename,
                    file_hash,
                    processed_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    file_url,
                    filename,
                    file_hash,
                    current_time()
                )
            )


# --------------------------------------------------
# Update day tracking
# --------------------------------------------------

def is_update_processed_today(update_date):
    """
    Check whether the specified India calendar day
    has already been processed.
    """

    with get_connection() as conn:

        if using_postgres():

            row = conn.execute(
                """
                SELECT 1
                FROM update_days
                WHERE update_date = %s
                """,
                (update_date,)
            ).fetchone()

        else:

            row = conn.execute(
                """
                SELECT 1
                FROM update_days
                WHERE update_date = ?
                """,
                (update_date,)
            ).fetchone()

    return row is not None


def save_update_day(update_date):
    """
    Mark an India calendar day as processed.
    """

    with get_connection() as conn:

        if using_postgres():

            conn.execute(
                """
                INSERT INTO update_days
                (
                    update_date,
                    processed_at
                )
                VALUES (%s, %s)
                ON CONFLICT (update_date) DO NOTHING
                """,
                (
                    update_date,
                    current_time()
                )
            )

        else:

            conn.execute(
                """
                INSERT OR IGNORE INTO update_days
                (
                    update_date,
                    processed_at
                )
                VALUES (?, ?)
                """,
                (
                    update_date,
                    current_time()
                )
            )
            
def get_overall_statistics():
    """
    Get statistics for all applications currently stored
    in the database.
    """

    with get_connection() as conn:

        if using_postgres():
            row = conn.execute("""
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (
                        WHERE LOWER(decision) = 'approved'
                    ) AS approved,
                    COUNT(*) FILTER (
                        WHERE LOWER(decision) = 'refused'
                    ) AS refused
                FROM applications
            """).fetchone()

        else:
            row = conn.execute("""
                SELECT
                    COUNT(*) AS total,
                    SUM(
                        CASE
                            WHEN LOWER(decision) = 'approved'
                            THEN 1 ELSE 0
                        END
                    ) AS approved,
                    SUM(
                        CASE
                            WHEN LOWER(decision) = 'refused'
                            THEN 1 ELSE 0
                        END
                    ) AS refused
                FROM applications
            """).fetchone()

    total = row[0] or 0
    approved = row[1] or 0
    refused = row[2] or 0

    approval_rate = (
        approved / total * 100
        if total > 0
        else 0
    )

    refusal_rate = (
        refused / total * 100
        if total > 0
        else 0
    )

    return {
        "total": total,
        "approved": approved,
        "refused": refused,
        "approval_rate": approval_rate,
        "refusal_rate": refusal_rate,
    }


def get_latest_update_statistics():
    """
    Get statistics for the most recent batch of
    newly detected visa decisions.
    """

    with get_connection() as conn:

        row = conn.execute("""
            SELECT
                detected_at,
                total_new,
                approved,
                refused
            FROM decision_updates
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()

    if not row:
        return None

    detected_at = row[0]
    total_new = row[1]
    approved = row[2]
    refused = row[3]

    approval_rate = (
        approved / total_new * 100
        if total_new > 0
        else 0
    )

    refusal_rate = (
        refused / total_new * 100
        if total_new > 0
        else 0
    )

    return {
        "detected_at": detected_at,
        "total_new": total_new,
        "approved": approved,
        "refused": refused,
        "approval_rate": approval_rate,
        "refusal_rate": refusal_rate,
    }


def get_update_history():
    """
    Get historical update statistics.
    """

    with get_connection() as conn:

        rows = conn.execute("""
            SELECT
                detected_at,
                total_new,
                approved,
                refused
            FROM decision_updates
            ORDER BY id ASC
        """).fetchall()

    return rows