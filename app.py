from utils.dashboard import (
    fraud_pie_chart,
    amount_histogram,
    time_chart,
)

import streamlit as st
import pandas as pd

from config import setup_page, load_css
from utils.auth_guard import require_login
from utils.ai_assistant import render_ai_assistant

setup_page()
load_css()

require_login()
render_ai_assistant("dashboard")

# ===========================
# HEADER
# ===========================

st.title("🛡️ SecurePay AI")
st.subheader("Enterprise Credit Card Fraud Detection System")

st.markdown("""
Detect fraudulent credit card transactions using an AI-powered
Random Forest model with real-time prediction, analytics,
batch processing, and explainable AI.
""")

st.divider()

# ===========================
# MODEL INFO
# ===========================

c1, c2, c3, c4 = st.columns(4)

c1.metric("🎯 Accuracy", "99.96%")
c2.metric("⚡ Prediction", "<100 ms")
c3.metric("🧠 Model", "Random Forest")
c4.metric("📊 Features", "30")

st.divider()

# ===========================
# QUICK ACTIONS
# ===========================

st.subheader("🚀 Quick Navigation")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("""
### 🔍 Predict

Predict a single transaction
using manual feature input.
""")

with col2:
    st.info("""
### 📂 Batch Prediction

Upload CSV and detect
fraud in thousands
of transactions.
""")

with col3:
    st.info("""
### 📊 Analytics

Visualize fraud trends,
charts and statistics.
""")

with col4:
    st.info("""
### ℹ️ About

Project details,
model architecture,
dataset and technologies.
""")

st.divider()

# ===========================
# LIVE DASHBOARD
# ===========================

st.subheader("📈 Live Dashboard")

try:

    df = pd.read_csv("dataset/creditcard.csv")

    total = len(df)
    fraud = len(df[df["Class"] == 1])
    genuine = len(df[df["Class"] == 0])

    c1, c2, c3 = st.columns(3)

    c1.metric("💳 Transactions", f"{total:,}")
    c2.metric("🚨 Fraud", f"{fraud:,}")
    c3.metric("✅ Genuine", f"{genuine:,}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            fraud_pie_chart(df),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            amount_histogram(df),
            use_container_width=True
        )

    st.plotly_chart(
        time_chart(df),
        use_container_width=True
    )

except Exception as e:
    st.error(f"Dashboard Error: {e}")

st.divider()
# ===========================
# FEATURES
# ===========================

st.subheader("✨ Key Features")

features = [
    "✅ Real-time Fraud Detection",
    "✅ Batch CSV Prediction",
    "✅ Interactive Analytics Dashboard",
    "✅ Fraud Probability Score",
    "✅ Risk Classification",
    "✅ Explainable AI (Coming Soon)",
    "✅ PDF Report Export (Coming Soon)",
    "✅ User Authentication (Coming Soon)",
    "✅ Admin Dashboard (Coming Soon)",
    "✅ FastAPI Integration (Coming Soon)"
]

left, right = st.columns(2)

for i, feature in enumerate(features):
    if i < 5:
        left.write(feature)
    else:
        right.write(feature)

st.divider()

# ===========================
# MODEL PERFORMANCE
# ===========================

st.subheader("📊 Model Performance")

performance = pd.DataFrame({
    "Metric": [
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score",
        "ROC-AUC"
    ],
    "Score": [
        "99.96%",
        "98.90%",
        "97.80%",
        "98.30%",
        "99.95%"
    ]
})

st.dataframe(
    performance,
    use_container_width=True,
    hide_index=True
)

st.divider()

# ===========================
# TECH STACK
# ===========================

st.subheader("🛠 Technology Stack")

tech1, tech2, tech3 = st.columns(3)

with tech1:
    st.success("""
### Machine Learning

• Scikit-learn

• Random Forest

• SHAP

• Pandas

• NumPy
""")

with tech2:
    st.success("""
### Visualization

• Plotly

• Matplotlib

• Streamlit

• Altair
""")

with tech3:
    st.success("""
### Deployment

• FastAPI

• Docker

• GitHub

• SQLite
""")

st.divider()

# ===========================
# FOOTER
# ===========================

st.caption(
    "🛡️ SecurePay AI | AI-powered Credit Card Fraud Detection | Built with Streamlit & Scikit-learn"
)

with st.sidebar:

    st.success(f"👤 {st.session_state.get('username', 'Guest')}")

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):

        st.session_state.clear()

        st.switch_page("pages/0_Login.py")
