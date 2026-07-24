import sqlite3
from pathlib import Path
import bcrypt

# Absolute path to the database
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "securepay.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_column(cursor, table_name, column_name, column_definition):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = {row["name"] for row in cursor.fetchall()}

    if column_name not in columns:
        cursor.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # ================= USERS =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Create default admin if it doesn't exist
    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        ("admin",)
    )

    if cursor.fetchone() is None:
        hashed = bcrypt.hashpw(
            "admin123".encode(),
            bcrypt.gensalt()
        ).decode()

        cursor.execute("""
        INSERT INTO users(username,email,password,role)
        VALUES(?,?,?,?)
        """, (
            "admin",
            "admin@securepay.ai",
            hashed,
            "admin"
        ))

    # ================= SINGLE PREDICTIONS =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        transaction_id TEXT,
        probability REAL,
        prediction TEXT,
        amount REAL,
        risk_level TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ================= BATCH PREDICTIONS =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS batch_predictions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        filename TEXT,
        total INTEGER,
        fraud INTEGER,
        genuine INTEGER,
        fraud_rate REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ================= PREDICTION HISTORY =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prediction_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        transaction_id TEXT,
        prediction TEXT,
        probability REAL,
        amount REAL,
        risk_level TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Keep older local databases compatible with the current app code.
    ensure_column(cursor, "users", "role", "TEXT DEFAULT 'user'")
    ensure_column(cursor, "users", "created_at", "TIMESTAMP")
    ensure_column(cursor, "predictions", "transaction_id", "TEXT")
    ensure_column(cursor, "predictions", "risk_level", "TEXT")
    ensure_column(cursor, "batch_predictions", "fraud_rate", "REAL")

    cursor.execute(
        "UPDATE users SET role = 'user' WHERE role IS NULL OR role = ''"
    )
    cursor.execute(
        "UPDATE users SET role = 'admin' WHERE username = ?",
        ("admin",)
    )

    conn.commit()
    conn.close()


create_tables()

