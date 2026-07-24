import bcrypt

from database.db import get_connection


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


def register(username, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    try:

        hashed = hash_password(password)

        print("=" * 50)
        print("REGISTER")
        print("Username:", username)
        print("Email:", email)
        print("Password:", password)
        print("Hash:", hashed)

        cursor.execute("""
        INSERT INTO users(username,email,password)
        VALUES(?,?,?)
        """, (
            username,
            email,
            hashed
        ))

        conn.commit()

        print("✅ Registration Successful")

        return True

    except Exception as e:

        print("REGISTER ERROR:", e)
        return False

    finally:
        
        conn.close()


def login(username, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    print("=" * 50)
    print("LOGIN ATTEMPT")
    print("Username entered:", username)
    print("Database row:", user)

    if user is None:
        print("❌ USER NOT FOUND")
        return False

    print("Stored username:", user["username"])
    print("Stored hash:", user["password"])

    try:
        result = verify_password(password, user["password"])
        print("Password matched:", result)
        return result
    except Exception as e:
        print("VERIFY ERROR:", e)
        return False