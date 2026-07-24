import streamlit as st

from config import setup_page, load_css
from database.auth import login, register
from utils.ai_assistant import render_ai_assistant

setup_page()
load_css()
render_ai_assistant("login")

if st.session_state.get("logged_in", False):
    st.switch_page("app.py")

st.title("🔐 SecurePay AI Login")

tab1, tab2 = st.tabs(["Login", "Register"])

# ---------------- LOGIN ---------------- #

with tab1:

    username = st.text_input(
        "Username",
        key="login_username"
    )

    password = st.text_input(
        "Password",
        type="password",
        key="login_password"
    )

    if st.button(
        "Login",
        key="login_button"
    ):

        if login(username, password):

            st.success("Login Successful")

            st.session_state.logged_in = True
            st.session_state.username = username

            st.switch_page("app.py")

        else:

            st.error("Invalid Credentials")


# ---------------- REGISTER ---------------- #

with tab2:

    new_user = st.text_input(
        "New Username",
        key="register_username"
    )

    email = st.text_input(
        "Email",
        key="register_email"
    )

    new_pass = st.text_input(
        "Password",
        type="password",
        key="register_password"
    )

    if st.button(
        "Register",
        key="register_button"
    ):

        if register(
            new_user,
            email,
            new_pass
        ):

            st.success("Account Created Successfully")

        else:

            st.error("Username or Email already exists")
