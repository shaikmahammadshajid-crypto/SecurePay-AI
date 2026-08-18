import os
import sqlite3

import bcrypt

from config import ADMIN_EMAIL, ADMIN_USERNAME, DATABASE_PATH


DB_PATH = DATABASE_PATH


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def ensure_column(cursor, table_name, column_name, column_definition):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = {row["name"] for row in cursor.fetchall()}
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}")


def _hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def seed_admin_account(cursor):
    password = os.getenv("SECUREPAY_ADMIN_PASSWORD")
    cursor.execute("SELECT id FROM users WHERE username = ?", (ADMIN_USERNAME,))
    existing = cursor.fetchone()

    if existing is None and password:
        cursor.execute(
            """
            INSERT INTO users(username, email, password, role)
            VALUES (?, ?, ?, 'admin')
            """,
            (ADMIN_USERNAME, ADMIN_EMAIL, _hash_password(password)),
        )
        return

    if existing is not None:
        cursor.execute("UPDATE users SET role = 'admin' WHERE username = ?", (ADMIN_USERNAME,))
        if password:
            cursor.execute(
                "UPDATE users SET password = ? WHERE username = ?",
                (_hash_password(password), ADMIN_USERNAME),
            )


def migrate_prediction_history(cursor):
    cursor.execute("SELECT COUNT(*) FROM predictions")
    prediction_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM prediction_history")
    history_count = cursor.fetchone()[0]
    if prediction_count or not history_count:
        return

    cursor.execute(
        """
        INSERT INTO predictions(
            username,
            transaction_id,
            prediction,
            probability,
            amount,
            risk_level,
            created_at
        )
        SELECT
            username,
            transaction_id,
            prediction,
            probability,
            amount,
            risk_level,
            created_at
        FROM prediction_history
        """
    )


def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            transaction_id TEXT,
            prediction TEXT,
            probability REAL,
            amount REAL,
            risk_level TEXT,
            model_name TEXT,
            features_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS prediction_history(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            transaction_id TEXT,
            prediction TEXT,
            probability REAL,
            amount REAL,
            risk_level TEXT,
            model_name TEXT,
            features_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS batch_predictions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            filename TEXT,
            total INTEGER,
            fraud INTEGER,
            genuine INTEGER,
            fraud_rate REAL,
            average_probability REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    ensure_column(cursor, "users", "role", "TEXT DEFAULT 'user'")
    ensure_column(cursor, "users", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    ensure_column(cursor, "predictions", "transaction_id", "TEXT")
    ensure_column(cursor, "predictions", "risk_level", "TEXT")
    ensure_column(cursor, "predictions", "model_name", "TEXT")
    ensure_column(cursor, "predictions", "features_json", "TEXT")
    ensure_column(cursor, "prediction_history", "model_name", "TEXT")
    ensure_column(cursor, "prediction_history", "features_json", "TEXT")
    ensure_column(cursor, "batch_predictions", "fraud_rate", "REAL")
    ensure_column(cursor, "batch_predictions", "average_probability", "REAL")

    cursor.execute("UPDATE users SET role = 'user' WHERE role IS NULL OR role = ''")
    seed_admin_account(cursor)
    migrate_prediction_history(cursor)
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_predictions_username_created_at "
        "ON predictions(username, created_at DESC)"
    )
    cursor.execute(
        "CREATE INDEX IF NOT EXISTS idx_batch_predictions_username_created_at "
        "ON batch_predictions(username, created_at DESC)"
    )

    conn.commit()
    conn.close()


create_tables()
