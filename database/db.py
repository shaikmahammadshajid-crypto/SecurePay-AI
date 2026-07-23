import sqlite3
from pathlib import Path

# Create database directory if it doesn't exist
Path("database").mkdir(exist_ok=True)

DB_PATH = Path("database/securepay.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    # ==========================
    # USERS TABLE
    # ==========================
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

    # ==========================
    # SINGLE PREDICTIONS
    # ==========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT NOT NULL,

        transaction_id TEXT,

        prediction TEXT,

        probability REAL,

        amount REAL,

        risk_level TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # ==========================
    # BATCH PREDICTIONS
    # ==========================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS batch_predictions(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        username TEXT NOT NULL,

        filename TEXT,

        total INTEGER,

        fraud INTEGER,

        genuine INTEGER,

        fraud_rate REAL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


create_tables()