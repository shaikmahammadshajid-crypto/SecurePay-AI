import streamlit as st


def require_login():
    """
    Prevent access if the user is not logged in.
    """

    if not st.session_state.get("logged_in", False):
        st.warning("🔐 Please login first.")
        st.switch_page("pages/0_Login.py")