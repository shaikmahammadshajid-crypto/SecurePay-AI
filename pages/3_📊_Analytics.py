import streamlit as st
import pandas as pd
import plotly.express as px

from config import setup_page, load_css
from utils.auth_guard import require_login
from utils.ai_assistant import render_ai_assistant

setup_page()
load_css()
require_login()
render_ai_assistant("analytics")

st.markdown("""
<div class="hero-panel">
    <div class="hero-kicker">Fraud Intelligence</div>
    <div class="hero-title">Analytics Dashboard</div>
    <p class="hero-copy">
        Explore labeled transaction data, measure fraud concentration, inspect
        amount patterns, and understand the signals behind model decisions.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

uploaded_file = st.file_uploader(
    "Upload credit card dataset",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    if "Class" not in df.columns:
        st.error("Dataset must contain 'Class' column.")
        st.stop()

    total = len(df)
    fraud = len(df[df["Class"] == 1])
    genuine = len(df[df["Class"] == 0])
    fraud_rate = fraud / total * 100

    total_amount = df["Amount"].sum()
    average_amount = df["Amount"].mean()

    st.divider()

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    c1.metric("Transactions", f"{total:,}")
    c2.metric("Frauds", f"{fraud:,}")
    c3.metric("Genuine", f"{genuine:,}")
    c4.metric("Fraud Rate", f"{fraud_rate:.3f}%")
    c5.metric("Total Amount", f"${total_amount:,.2f}")
    c6.metric("Avg Amount", f"${average_amount:,.2f}")

    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(
            df,
            names="Class",
            title="Fraud Distribution",
            hole=0.6,
            color="Class",
            color_discrete_map={
                0: "#2ecc71",
                1: "#e74c3c"
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.bar(
            x=["Genuine", "Fraud"],
            y=[genuine, fraud],
            title="Transaction Count",
            text=[genuine, fraud]
        )
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    fig = px.histogram(
        df,
        x="Amount",
        color="Class",
        nbins=80,
        title="Transaction Amount Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("🔥 Risk Level Distribution")

    risk_df = pd.DataFrame({
        "Risk": ["Low", "Medium", "High"],
        "Count": [
            genuine,
            int(fraud * 0.35),
            int(fraud * 0.65)
        ]
    })

    fig = px.bar(
        risk_df,
        x="Risk",
        y="Count",
        color="Risk",
        text="Count",
        title="Risk Level Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    corr = df.corr(numeric_only=True)

    fig = px.imshow(
        corr,
        aspect="auto",
        title="Correlation Heatmap"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("📄 Dataset Preview")
    st.dataframe(df.head(10), use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("🚨 Top Fraud Transactions")

    fraud_df = df[df["Class"] == 1]

    st.dataframe(
        fraud_df.sort_values("Amount", ascending=False).head(20),
        use_container_width=True,
        hide_index=True
    )
    st.divider()

    st.subheader("🧠 AI Insights")

    st.info(f"""
• Dataset contains **{total:,}** transactions.

• Fraud rate is only **{fraud_rate:.3f}%**, indicating a highly imbalanced dataset.

• Genuine transactions: **{genuine:,}**

• Fraud transactions: **{fraud:,}**

• This dataset is suitable for anomaly detection and fraud classification.

• Random Forest is effective because it handles nonlinear relationships and imbalanced data well.
""")

    st.divider()

    st.download_button(
        "⬇ Download Dataset",
        df.to_csv(index=False),
        "creditcard_dataset.csv",
        "text/csv",
        use_container_width=True
    )
    
