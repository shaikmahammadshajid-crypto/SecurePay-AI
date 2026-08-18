import json

from database.db import create_tables, get_connection


def save_prediction(
    username,
    transaction_id,
    prediction,
    probability,
    amount,
    risk_level,
    model_name=None,
    features=None,
):
    create_tables()
    features_json = json.dumps(features) if features is not None else None
    probability_value = None if probability is None else float(probability)

    conn = get_connection()
    cursor = conn.cursor()
    values = (
        username,
        transaction_id,
        prediction,
        probability_value,
        float(amount),
        risk_level,
        model_name,
        features_json,
    )

    cursor.execute(
        """
        INSERT INTO predictions(
            username,
            transaction_id,
            prediction,
            probability,
            amount,
            risk_level,
            model_name,
            features_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        values,
    )
    row_id = cursor.lastrowid

    cursor.execute(
        """
        INSERT INTO prediction_history(
            username,
            transaction_id,
            prediction,
            probability,
            amount,
            risk_level,
            model_name,
            features_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        values,
    )

    conn.commit()
    conn.close()
    return row_id


def _rows(query, params=()):
    create_tables()
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def get_user_history(username, limit=None):
    query = """
        SELECT
            id,
            username,
            transaction_id,
            prediction,
            probability,
            amount,
            risk_level,
            model_name,
            features_json,
            created_at
        FROM predictions
        WHERE username = ?
        ORDER BY created_at DESC, id DESC
    """
    params = [username]
    if limit:
        query += " LIMIT ?"
        params.append(int(limit))
    return _rows(query, params)


def get_prediction_history(username=None, limit=None):
    query = """
        SELECT
            id,
            username,
            transaction_id,
            prediction,
            probability,
            amount,
            risk_level,
            model_name,
            created_at
        FROM predictions
    """
    params = []
    if username:
        query += " WHERE username = ?"
        params.append(username)
    query += " ORDER BY created_at DESC, id DESC"
    if limit:
        query += " LIMIT ?"
        params.append(int(limit))
    return _rows(query, params)


def get_prediction_by_id(prediction_id, username=None):
    query = """
        SELECT *
        FROM predictions
        WHERE id = ?
    """
    params = [int(prediction_id)]
    if username:
        query += " AND username = ?"
        params.append(username)

    rows = _rows(query, params)
    return rows[0] if rows else None


def decode_features(row):
    if row is None or not row["features_json"]:
        return None
    try:
        return json.loads(row["features_json"])
    except (TypeError, json.JSONDecodeError):
        return None
