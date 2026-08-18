import database.auth as auth
import database.db as db


def use_temp_database(tmp_path):
    db.DB_PATH = tmp_path / "securepay_test.db"
    db.create_tables()


def test_register_rejects_invalid_email(tmp_path):
    use_temp_database(tmp_path)

    success, message = auth.register_account("Alice", "not-an-email", "secret1")

    assert success is False
    assert message == "Enter a valid email address."


def test_register_and_authenticate_normalizes_username(tmp_path):
    use_temp_database(tmp_path)

    success, _ = auth.register_account("Alice", "Alice@example.com", "secret1")
    user = auth.authenticate(" ALICE ", "secret1")

    assert success is True
    assert user is not None
    assert user["username"] == "alice"
    assert auth.login("alice", "wrong-password") is False


def test_password_hash_is_not_plaintext(tmp_path):
    use_temp_database(tmp_path)

    auth.register_account("Bob", "bob@example.com", "secret1")

    conn = db.get_connection()
    row = conn.execute("SELECT password FROM users WHERE username = ?", ("bob",)).fetchone()
    conn.close()

    assert row["password"] != "secret1"
    assert row["password"].startswith("$2")
