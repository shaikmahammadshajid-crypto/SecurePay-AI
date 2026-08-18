import logging
import re
import sqlite3

import bcrypt

from database.db import get_connection


logger = logging.getLogger(__name__)

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_.-]{2,31}$")
VALID_ROLES = {"user", "admin"}
MINIMUM_PASSWORD_LENGTH = 8
MAXIMUM_BCRYPT_PASSWORD_BYTES = 72


def normalize_username(username):
    return (username or "").strip().lower()


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def register_account(username, email, password):
    username = normalize_username(username)
    email = (email or "").strip().lower()

    if not username or not email or not password:
        return False, "Username, email, and password are required."

    if not USERNAME_PATTERN.fullmatch(username):
        return (
            False,
            "Username must be 3-32 characters and use lowercase letters, numbers, dots, hyphens, or underscores.",
        )

    if len(password) < MINIMUM_PASSWORD_LENGTH:
        return False, f"Password must be at least {MINIMUM_PASSWORD_LENGTH} characters."

    if len(password.encode("utf-8")) > MAXIMUM_BCRYPT_PASSWORD_BYTES:
        return False, "Password is too long. Use at most 72 UTF-8 bytes."

    if len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
        return False, "Enter a valid email address."

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users(username, email, password, role)
            VALUES (?, ?, ?, 'user')
            """,
            (username, email, hash_password(password)),
        )
        conn.commit()
        logger.info("Registered new SecurePay AI user: %s", username)
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "Username or email already exists."
    except Exception:
        logger.exception("Registration failed for username=%s", username)
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
        "SELECT id, username, email, password, role, created_at FROM users WHERE username = ?",
        (username,),
    )
    user = cursor.fetchone()
    conn.close()

    if user is None:
        logger.info("Authentication failed for username=%s", username)
        return None

    try:
        if verify_password(password, user["password"]):
            if user["role"] not in VALID_ROLES:
                logger.warning("Unsupported role blocked at login for username=%s role=%s", username, user["role"])
                return None
            logger.info("Authentication succeeded for username=%s role=%s", username, user["role"])
            return user
    except Exception:
        logger.exception("Password verification failed for username=%s", username)
        return None

    logger.info("Authentication failed for username=%s", username)
    return None


def login(username, password):
    return authenticate(username, password) is not None
