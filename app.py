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
from utils.demo_data import load_dashboard_data

setup_page()
load_css()

require_login()
render_ai_assistant("dashboard")

# ===========================
# HEADER
# ===========================

st.markdown("""
<div class="hero-panel">
    <div class="hero-kicker">Live Fraud Operations Workspace</div>
    <div class="hero-title">SecurePay AI</div>
    <p class="hero-copy">
        Score suspicious payments, investigate risk, export evidence, and monitor
        transaction activity from one analyst-friendly dashboard.
    </p>
    <div class="status-strip">
        <div class="status-pill"><strong>99.96%</strong><span>Model accuracy</span></div>
        <div class="status-pill"><strong>&lt;100 ms</strong><span>Single prediction</span></div>
        <div class="status-pill"><strong>30</strong><span>Transaction signals</span></div>
        <div class="status-pill"><strong>SQLite</strong><span>Audit storage</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ===========================
# MODEL INFO
# ===========================

c1, c2, c3, c4 = st.columns(4)

c1.metric("Accuracy", "99.96%")
c2.metric("Prediction", "<100 ms")
c3.metric("Model", "Random Forest")
c4.metric("Features", "30")

st.divider()

# ===========================
# QUICK ACTIONS
# ===========================

st.subheader("Analyst Workflow")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
<div class="section-card">
    <h3>Score One Payment</h3>
    <p>Run a single transaction through the model and get fraud-response guidance.</p>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/1_💳_Predict.py", label="Open Predict")

with col2:
    st.markdown("""
<div class="section-card">
    <h3>Screen a Batch</h3>
    <p>Upload a CSV, classify every row, and prioritize cases for review.</p>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/2_📂_Batch_Prediction.py", label="Open Batch")

with col3:
    st.markdown("""
<div class="section-card">
    <h3>Investigate Trends</h3>
    <p>Use charts and distributions to understand fraud behavior in labeled data.</p>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/3_📊_Analytics.py", label="Open Analytics")

with col4:
    st.markdown("""
<div class="section-card">
    <h3>Review the System</h3>
    <p>See the architecture, model details, dataset format, and project scope.</p>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/4_ℹ️_About.py", label="Open About")

st.divider()

# ===========================
# LIVE DASHBOARD
# ===========================

st.subheader("Live Risk Dashboard")

try:

    df, is_demo_data = load_dashboard_data()

    total = len(df)
    fraud = len(df[df["Class"] == 1])
    genuine = len(df[df["Class"] == 0])

    c1, c2, c3 = st.columns(3)

    fraud_rate = fraud / total * 100

    c1.metric("Transactions", f"{total:,}")
    c2.metric("Fraud Cases", f"{fraud:,}")
    c3.metric("Genuine Cases", f"{genuine:,}")

    st.markdown(f"""
<div class="trust-band">
    <p><strong>Operational note:</strong> Fraud appears in {fraud_rate:.3f}% of this dataset.
    This is realistic for card payments, so analysts should review probability, risk level,
    and explainability instead of relying on accuracy alone.</p>
</div>
""", unsafe_allow_html=True)

    if is_demo_data:
        st.info(
            "Public demo mode: dashboard charts are using generated sample transactions "
            "because the full dataset is not included in the GitHub deployment."
        )

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

st.subheader("Production-Oriented Capabilities")

features = [
    "✅ Real-time Fraud Detection",
    "✅ Batch CSV Prediction",
    "✅ Interactive Analytics Dashboard",
    "✅ Fraud Probability Score",
    "✅ Risk Classification",
    "✅ AI Fraud Analyst Recommendations",
    "✅ PDF Report Export",
    "✅ User Authentication",
    "✅ Admin Dashboard",
    "✅ Prediction History"
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
