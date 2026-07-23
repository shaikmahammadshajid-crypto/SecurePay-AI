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

        cursor.execute("""
        INSERT INTO users(
        username,
        email,
        password
        )

        VALUES(?,?,?)
        """, (

            username,
            email,
            hash_password(password)

        ))

        conn.commit()

        return True

    except:

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

    if user is None:
        print("❌ User not found")
        return False

    print("✅ User found:", user["username"])
    print("Stored Hash:", user["password"])

    result = verify_password(password, user["password"])

    print("Password Match:", result)

    return result