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
        probability REAL,
        prediction TEXT,
        amount REAL,
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


create_tables()