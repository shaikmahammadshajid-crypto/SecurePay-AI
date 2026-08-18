from pathlib import Path

from database.db import DB_PATH, get_connection
from utils.model_loader import MODEL_PATH, SCALER_PATH


def get_app_health(username=None):
    checks = [
        file_check("Model artifact", MODEL_PATH),
        file_check("Scaler artifact", SCALER_PATH),
    ]

    checks.append(database_check())

    if username:
        checks.append(user_history_check(username))

    return checks


def file_check(name, path):
    artifact = Path(path)
    if artifact.exists() and artifact.stat().st_size > 0:
        return {
            "name": name,
            "ok": True,
            "detail": f"{artifact.as_posix()} is available.",
        }

    return {
        "name": name,
        "ok": False,
        "detail": f"{artifact.as_posix()} is missing or empty.",
    }


def database_check():
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
    except Exception as exc:
        return {
            "name": "SQLite database",
            "ok": False,
            "detail": f"{DB_PATH.as_posix()} is not reachable: {exc}",
        }

    return {
        "name": "SQLite database",
        "ok": True,
        "detail": f"{DB_PATH.as_posix()} is reachable.",
    }


def user_history_check(username):
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM prediction_history WHERE username = ?",
        (username,),
    ).fetchone()[0]
    conn.close()

    return {
        "name": "User prediction history",
        "ok": True,
        "detail": f"{count} saved predictions for {username}.",
    }


def health_summary(checks):
    failed = [check for check in checks if not check["ok"]]

    if failed:
        return {
            "status": "attention",
            "message": f"{len(failed)} check needs attention.",
        }

    return {
        "status": "ok",
        "message": f"{len(checks)} checks passed.",
    }
