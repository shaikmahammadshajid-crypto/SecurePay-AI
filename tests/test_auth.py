import database.auth as auth
import database.db as db


def use_temp_database(tmp_path):
    db.DB_PATH = tmp_path / "securepay_test.db"
    db.create_tables()


def test_register_rejects_invalid_email(tmp_path):
    use_temp_database(tmp_path)

    success, message = auth.register_account("Alice", "not-an-email", "secure123")

    assert success is False
    assert message == "Enter a valid email address."


def test_register_and_authenticate_normalizes_username(tmp_path):
    use_temp_database(tmp_path)

    success, _ = auth.register_account("Alice", "Alice@example.com", "secure123")
    user = auth.authenticate(" ALICE ", "secure123")

    assert success is True
    assert user is not None
    assert user["username"] == "alice"
    assert auth.login("alice", "wrong-password") is False


def test_password_hash_is_not_plaintext(tmp_path):
    use_temp_database(tmp_path)

    auth.register_account("Bob", "bob@example.com", "secure123")

    conn = db.get_connection()
    row = conn.execute("SELECT password FROM users WHERE username = ?", ("bob",)).fetchone()
    conn.close()

    assert row["password"] != "secure123"
    assert row["password"].startswith("$2")


def test_register_rejects_an_invalid_username_and_short_password(tmp_path):
    use_temp_database(tmp_path)

    invalid_username, username_message = auth.register_account("not allowed", "user@example.com", "secure123")
    short_password, password_message = auth.register_account("valid_user", "user@example.com", "short")

    assert invalid_username is False
    assert "Username must be" in username_message
    assert short_password is False
    assert password_message == "Password must be at least 8 characters."
