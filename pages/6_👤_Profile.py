import streamlit as st
import pandas as pd

from config import setup_page, load_css
from utils.auth_guard import require_login
from utils.ai_assistant import render_ai_assistant
from database.profile import get_user_profile
from database.history import get_user_history

setup_page()
load_css()
require_login()
render_ai_assistant("profile")

st.title("👤 My Profile")

username = st.session_state.get("username")

user = get_user_profile(username)
history = get_user_history(username)

if user is None:
    st.error("User profile not found.")
    st.stop()

total_predictions = len(history)

fraud_count = 0

if total_predictions > 0:
    df = pd.DataFrame([dict(row) for row in history])

    if "prediction" in df.columns:
        fraud_count = (
            df["prediction"] == "🚨 Fraud Transaction"
        ).sum()

col1, col2 = st.columns(2)

with col1:
    st.info("### Account Details")

    st.write(f"**Username:** {user['username']}")
    st.write(f"**Email:** {user['email']}")
    st.write(f"**Role:** {user['role']}")
    st.write(f"**Joined:** {user['created_at']}")

with col2:
    st.info("### Prediction Statistics")

    st.metric(
        "Total Predictions",
        total_predictions
    )

    st.metric(
        "Fraud Transactions",
        fraud_count
    )

    genuine = total_predictions - fraud_count

    st.metric(
        "Genuine Transactions",
        genuine
    )

st.divider()

st.subheader("Recent Prediction History")

if total_predictions == 0:

    st.info("No prediction history available.")

else:

    history_df = pd.DataFrame([dict(row) for row in history])

    history_df = history_df.rename(columns={
        "transaction_id": "Transaction ID",
        "prediction": "Prediction",
        "probability": "Probability (%)",
        "amount": "Amount",
        "risk_level": "Risk Level",
        "created_at": "Date",
    })

    columns_to_show = [
        "Transaction ID",
        "Prediction",
        "Probability (%)",
        "Amount",
        "Risk Level",
        "Date",
    ]

    available_columns = [
        col for col in columns_to_show
        if col in history_df.columns
    ]

    st.dataframe(
        history_df[available_columns],
        use_container_width=True,
        hide_index=True,
    )
