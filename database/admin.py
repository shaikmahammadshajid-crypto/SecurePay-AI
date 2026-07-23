from database.db import get_connection


def get_all_users():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, username, email, role, created_at
    FROM users
    ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_all_predictions():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM predictions
    ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows


def get_dashboard_stats():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions")
    predictions = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM predictions
        WHERE prediction LIKE '%Fraud%'
    """)
    frauds = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM batch_predictions")
    batches = cursor.fetchone()[0]

    conn.close()

    return {
        "users": users,
        "predictions": predictions,
        "frauds": frauds,
        "batches": batches
    }