import streamlit as st

from config import setup_page, load_css
from database.auth import authenticate, normalize_username, register_account
from utils.ai_assistant import render_ai_assistant

setup_page()
load_css()
render_ai_assistant("login")

if st.session_state.get("logged_in", False):
    st.switch_page("app.py")

st.markdown("""
<div class="hero-panel">
    <div class="hero-kicker">Secure Fraud Workspace</div>
    <div class="hero-title">Access SecurePay AI</div>
    <p class="hero-copy">
        Sign in to score transactions, investigate model risk, export reports,
        and keep a searchable audit history for fraud review.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

left, right = st.columns([1.15, 0.85])

with left:
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

            user = authenticate(username, password)

            if user is not None:

                st.success("Login Successful")

                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.role = user["role"]

                st.switch_page("app.py")

            else:

                st.error("Invalid credentials. Check your username and password.")


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
            key="register_password",
            help="Use at least 6 characters."
        )

        if st.button(
            "Create Account",
            key="register_button"
        ):

            success, message = register_account(
                new_user,
                email,
                new_pass
            )

            if success:

                st.success("Account created successfully. Logging you in...")

                st.session_state.logged_in = True
                st.session_state.username = normalize_username(new_user)
                st.session_state.role = "user"

                st.switch_page("app.py")

            else:

                st.error(message)

with right:
    st.markdown("""
<div class="login-visual">
    <h3>Real-time Risk Console</h3>
    <p>Live fraud signals are scored, prioritized, and routed to analyst review.</p>
    <div class="visual-grid">
        <span class="visual-bar"></span>
        <span class="visual-bar"></span>
        <span class="visual-bar"></span>
        <span class="visual-bar"></span>
    </div>
    <div class="signal-row">
        <span>Velocity</span>
        <span>Amount</span>
        <span>Identity</span>
        <span>Risk</span>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="section-card">
    <h3>Built for Real Review</h3>
    <p>Every signed-in analyst can score payments, save prediction history,
    download reports, and use the AI assistant for fraud-response guidance.</p>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="section-card">
    <h3>Credential Behavior</h3>
    <p>New accounts sign in immediately. Usernames are normalized to lowercase
    and passwords are stored as bcrypt hashes.</p>
</div>
""", unsafe_allow_html=True)

    st.info(
        "Admin access is owner-controlled. Set `SECUREPAY_ADMIN_PASSWORD` "
        "before deployment to create an admin account."
    )
