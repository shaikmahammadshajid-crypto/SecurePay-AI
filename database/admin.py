from database.db import get_connection


def _fetchall(query, params=()):
    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows


def _fetchone(query, params=()):
    conn = get_connection()
    row = conn.execute(query, params).fetchone()
    conn.close()
    return row


def get_all_users():
    return _fetchall(
        """
        SELECT id, username, email, role, created_at
        FROM users
        ORDER BY created_at DESC, id DESC
        """
    )


def get_all_predictions(limit=None):
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
        ORDER BY created_at DESC, id DESC
    """
    params = []
    if limit:
        query += " LIMIT ?"
        params.append(int(limit))
    return _fetchall(query, params)


def get_dashboard_stats(username=None):
    where = "WHERE username = ?" if username else ""
    params = (username,) if username else ()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]

    cursor.execute(f"SELECT COUNT(*) FROM predictions {where}", params)
    predictions = cursor.fetchone()[0]

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM predictions
        {where}
        {'AND' if where else 'WHERE'} prediction LIKE '%Fraud%'
        """,
        params,
    )
    frauds = cursor.fetchone()[0]

    cursor.execute(f"SELECT COALESCE(AVG(probability), 0) FROM predictions {where}", params)
    average_probability = cursor.fetchone()[0]

    cursor.execute(f"SELECT COALESCE(AVG(amount), 0) FROM predictions {where}", params)
    average_amount = cursor.fetchone()[0]

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM predictions
        {where}
        {'AND' if where else 'WHERE'} (risk_level = 'HIGH' OR risk_level = 'CRITICAL')
        """,
        params,
    )
    high_risk = cursor.fetchone()[0]

    if username:
        cursor.execute("SELECT COUNT(*) FROM batch_predictions WHERE username = ?", (username,))
    else:
        cursor.execute("SELECT COUNT(*) FROM batch_predictions")
    batches = cursor.fetchone()[0]

    conn.close()

    genuine = predictions - frauds
    return {
        "users": users,
        "predictions": predictions,
        "frauds": frauds,
        "genuine": genuine,
        "batches": batches,
        "high_risk": high_risk,
        "fraud_rate": round((frauds / predictions) * 100, 2) if predictions else 0,
        "average_probability": round(float(average_probability or 0), 2),
        "average_amount": round(float(average_amount or 0), 2),
    }


def get_risk_distribution(username=None):
    where = "WHERE username = ?" if username else ""
    params = (username,) if username else ()
    return [
        dict(row)
        for row in _fetchall(
            f"""
            SELECT
                COALESCE(risk_level, 'UNAVAILABLE') AS risk_level,
                COUNT(*) AS total,
                ROUND(COALESCE(AVG(probability), 0), 2) AS average_probability
            FROM predictions
            {where}
            GROUP BY COALESCE(risk_level, 'UNAVAILABLE')
            ORDER BY
                CASE
                    WHEN risk_level = 'CRITICAL' THEN 1
                    WHEN risk_level = 'HIGH' THEN 2
                    WHEN risk_level = 'MEDIUM' THEN 3
                    WHEN risk_level = 'LOW' THEN 4
                    ELSE 5
                END
            """,
            params,
        )
    ]


def get_recent_batches(username=None, limit=10):
    where = "WHERE username = ?" if username else ""
    params = [username] if username else []
    params.append(int(limit))
    return [
        dict(row)
        for row in _fetchall(
            f"""
            SELECT
                id,
                username,
                filename,
                total,
                fraud,
                genuine,
                fraud_rate,
                average_probability,
                created_at
            FROM batch_predictions
            {where}
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            params,
        )
    ]


def save_batch_prediction(username, filename, total, fraud, genuine, fraud_rate, average_probability):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO batch_predictions(
            username,
            filename,
            total,
            fraud,
            genuine,
            fraud_rate,
            average_probability
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            filename,
            int(total),
            int(fraud),
            int(genuine),
            float(fraud_rate),
            None if average_probability is None else float(average_probability),
        ),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def update_user_role(user_id, role):
    if role not in {"user", "admin"}:
        raise ValueError("Unsupported role.")

    conn = get_connection()
    cursor = conn.cursor()
    if role == "user":
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        cursor.execute("SELECT role FROM users WHERE id = ?", (int(user_id),))
        target = cursor.fetchone()
        if target and target["role"] == "admin" and admin_count <= 1:
            conn.close()
            raise ValueError("At least one admin account must remain.")

    cursor.execute("UPDATE users SET role = ? WHERE id = ?", (role, int(user_id)))
    conn.commit()
    changed = cursor.rowcount
    conn.close()
    return changed > 0
