import streamlit as st
from database.db import get_connection


def require_admin():
    """
    Allows access only to logged-in admin users.
    """

    # Check login
    if not st.session_state.get("logged_in", False):
        st.warning("🔐 Please login first.")
        st.stop()

    username = st.session_state.get("username")

    if not username:
        st.error("Invalid session.")
        st.stop()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()
    conn.close()

    if user is None:
        st.error("User not found.")
        st.stop()

    if user["role"] != "admin":
        st.error("🚫 Access Denied! Administrator privileges required.")
        st.stop()