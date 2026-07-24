import bcrypt
import sqlite3

from database.db import get_connection


def normalize_username(username):
    return username.strip().lower()


def hash_password(password):

    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()


def verify_password(password, hashed):

    return bcrypt.checkpw(
        password.encode(),
        hashed.encode()
    )


def register_account(username, email, password):
    username = normalize_username(username)
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "Username, email, and password are required."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    conn = get_connection()
    cursor = conn.cursor()

    try:

        hashed = hash_password(password)

        cursor.execute("""
        INSERT INTO users(username,email,password)
        VALUES(?,?,?)
        """, (
            username,
            email,
            hashed
        ))

        conn.commit()

        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        return False, "Username or email already exists."

    except Exception:
        return False, "Unable to create account. Please try again."

    finally:
        conn.close()


def register(username, email, password):
    success, _ = register_account(username, email, password)
    return success


def authenticate(username, password):
    username = normalize_username(username)

    if not username or not password:
        return None

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:
        return None

    try:
        if verify_password(password, user["password"]):
            return user
    except Exception:
        return None

    return None


def login(username, password):
    return authenticate(username, password) is not None
