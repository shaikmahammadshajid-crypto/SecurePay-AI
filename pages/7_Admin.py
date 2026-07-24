import streamlit as st
import pandas as pd

from config import setup_page, load_css
from utils.admin_guard import require_admin
from utils.ai_assistant import render_ai_assistant
from database.admin import (
    get_all_users,
    get_all_predictions,
    get_dashboard_stats,
)

setup_page()
load_css()
require_admin()
render_ai_assistant("admin")

st.title("🛠 SecurePay AI Admin Dashboard")

# ================= DASHBOARD STATS =================

stats = get_dashboard_stats()

c1, c2, c3, c4 = st.columns(4)

c1.metric("👥 Users", stats["users"])
c2.metric("📊 Predictions", stats["predictions"])
c3.metric("🚨 Frauds", stats["frauds"])
c4.metric("📂 Batch Jobs", stats["batches"])

st.divider()

# ================= USERS =================

st.subheader("👥 Registered Users")

users = get_all_users()

if users:

    users_df = pd.DataFrame([dict(row) for row in users])

    users_df = users_df.rename(columns={
        "id": "User ID",
        "username": "Username",
        "email": "Email",
        "role": "Role",
        "created_at": "Created At",
    })

    st.dataframe(
        users_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "⬇ Download Users CSV",
        users_df.to_csv(index=False),
        "users.csv",
        "text/csv",
    )

else:

    st.info("No users found.")

st.divider()

# ================= PREDICTION LOGS =================

st.subheader("📜 Prediction Logs")

logs = get_all_predictions()

if logs:

    logs_df = pd.DataFrame([dict(row) for row in logs])

    logs_df = logs_df.rename(columns={
        "id": "ID",
        "username": "Username",
        "transaction_id": "Transaction ID",
        "prediction": "Prediction",
        "probability": "Probability (%)",
        "amount": "Amount",
        "risk_level": "Risk Level",
        "created_at": "Date",
    })

    st.dataframe(
        logs_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "⬇ Download Prediction Logs",
        logs_df.to_csv(index=False),
        "prediction_logs.csv",
        "text/csv",
    )

else:

    st.info("No predictions available.")
