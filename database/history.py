from database.db import get_connection


def create_history_table():

    conn = get_connection()
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()


def save_prediction(
    username,
    transaction_id,
    prediction,
    probability,
    amount,
    risk_level,
):

    create_history_table()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO prediction_history
        (
            username,
            transaction_id,
            prediction,
            probability,
            amount,
            risk_level
        )
        VALUES
        (?, ?, ?, ?, ?, ?)
    """,
    (
        username,
        transaction_id,
        prediction,
        probability,
        amount,
        risk_level
    ))

    conn.commit()
    conn.close()


def get_user_history(username):

    create_history_table()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM prediction_history
        WHERE username=?
        ORDER BY id DESC
    """,
    (username,))

    rows = cursor.fetchall()

    conn.close()

    return rows