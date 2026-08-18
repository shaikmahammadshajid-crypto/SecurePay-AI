from pathlib import Path

from config import DATABASE_PATH, MODEL_PATH, SCALER_PATH
from database.db import get_connection
from utils.model_loader import get_model_info


def get_app_health(username=None):
    checks = [
        file_check("Random Forest model artifact", MODEL_PATH),
        file_check("StandardScaler artifact", SCALER_PATH),
        database_check(),
        model_interface_check(),
    ]

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
            "detail": f"{DATABASE_PATH.as_posix()} is not reachable: {exc}",
        }

    return {
        "name": "SQLite database",
        "ok": True,
        "detail": f"{DATABASE_PATH.as_posix()} is reachable.",
    }


def model_interface_check():
    info = get_model_info()
    if info["status"] == "Ready":
        probability = "with probability output" if info["probability_supported"] else "without probability output"
        return {
            "name": "Model interface",
            "ok": True,
            "detail": f"{info['model_type']} is ready for {info['feature_count']} features {probability}.",
        }

    return {
        "name": "Model interface",
        "ok": False,
        "detail": info.get("error", "Model interface is unavailable."),
    }


def user_history_check(username):
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM predictions WHERE username = ?",
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
