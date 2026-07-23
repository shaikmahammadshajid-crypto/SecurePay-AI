from utils.explainability import show_shap_explanation
import uuid

import streamlit as st
import pandas as pd

from config import setup_page, load_css

from utils.auth_guard import require_login
from utils.model_loader import load_model, load_scaler
from utils.prediction import predict_transaction
from utils.charts import fraud_gauge

from utils.helpers import (
    get_prediction_text,
    get_risk_level,
    get_recommendation,
    probability_to_percentage,
)

from database.history import save_prediction
from reports.pdf_generator import generate_prediction_report


# -----------------------------
# Page Setup
# -----------------------------

setup_page()
load_css()

require_login()

model = load_model()
scaler = load_scaler()

# -----------------------------
# Header
# -----------------------------

st.title("💳 SecurePay AI")
st.caption("AI Powered Credit Card Fraud Detection System")

st.divider()

# -----------------------------
# Sidebar
# -----------------------------

with st.sidebar:

    st.success("✅ AI Model Loaded")

    st.info("Random Forest Classifier")

    st.markdown("### Model Information")

    st.write("- Dataset : Credit Card Fraud")
    st.write("- Features : 30")
    st.write("- Output : Fraud / Genuine")
    st.write("- Scaler : StandardScaler")

# -----------------------------
# Transaction Details
# -----------------------------

st.subheader("💳 Transaction Details")

col1, col2 = st.columns(2)

with col1:

    time = st.number_input(
        "Time",
        min_value=0.0,
        value=0.0,
        step=1.0
    )

with col2:

    amount = st.number_input(
        "Amount",
        min_value=0.0,
        value=100.0,
        step=1.0
    )

st.write("")

# -----------------------------
# Advanced Features
# -----------------------------

with st.expander("⚙ Advanced Features (V1 - V28)"):

    feature_values = []

    feature_names = [f"V{i}" for i in range(1,29)]

    cols = st.columns(4)

    for i, feature in enumerate(feature_names):

        with cols[i % 4]:

            value = st.number_input(
                feature,
                value=0.0,
                format="%.6f",
                key=feature
            )

            feature_values.append(value)

st.write("")

predict_button = st.button(
    "🚀 Predict Transaction",
    use_container_width=True
)
if predict_button:

    with st.spinner("🔍 Analyzing Transaction..."):

        input_data = [time]
        input_data.extend(feature_values)
        input_data.append(amount)

        prediction, probability = predict_transaction(
            model,
            scaler,
            input_data,
        )

        prediction_text = get_prediction_text(prediction)
        risk_level = get_risk_level(probability)
        recommendation = get_recommendation(probability)

        probability_percent = probability_to_percentage(probability)

        transaction_id = str(uuid.uuid4())[:8]

        save_prediction(
            username=st.session_state.username,
            transaction_id=transaction_id,
            prediction=prediction_text,
            probability=probability_percent,
            amount=amount,
            risk_level=risk_level,
        )

    st.success("✅ Prediction Completed Successfully!")

    st.toast("Prediction saved successfully.")

    st.divider()

    st.subheader("📊 Prediction Result")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Prediction", prediction_text)

    with c2:
        st.metric("Fraud Probability", f"{probability_percent}%")

    with c3:
        st.metric("Risk Level", risk_level)

    st.progress(probability)

    st.info(f"💡 Recommendation: {recommendation}")

    st.divider()

    st.subheader("🤖 AI Recommendation")

    if prediction == 1:

        st.error("""
🚨 High Risk Transaction

Recommended Actions

• Block the transaction immediately.

• Contact the customer.

• Verify customer identity.

• Review recent account activity.

• Flag this account for manual investigation.

• Notify the fraud monitoring team.
""")

    else:

        st.success("""
✅ Genuine Transaction

Recommended Actions

• Approve the transaction.

• Continue normal processing.

• No immediate action required.

• Continue monitoring future transactions.
""")

    fig = fraud_gauge(probability)

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.divider()

    st.subheader("🧠 Explainable AI")

    feature_columns = [
        "Time",
        "V1","V2","V3","V4","V5","V6","V7","V8","V9",
        "V10","V11","V12","V13","V14","V15","V16","V17",
        "V18","V19","V20","V21","V22","V23","V24","V25",
        "V26","V27","V28","Amount"
    ]

    input_df = pd.DataFrame(
        [input_data],
        columns=feature_columns
    )

    show_shap_explanation(
        model,
        input_df,
    )
    st.divider()

    # -----------------------------
    # Prediction Summary
    # -----------------------------

    result_df = pd.DataFrame(
        {
            "Metric": [
                "Prediction",
                "Fraud Probability",
                "Risk Level",
                "Recommendation",
            ],
            "Value": [
                prediction_text,
                f"{probability_percent} %",
                risk_level,
                recommendation,
            ],
        }
    )

    st.subheader("📋 Prediction Summary")

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    # -----------------------------
    # PDF Report
    # -----------------------------

    try:

        pdf_file = generate_prediction_report(
            username=st.session_state.get("username", "Guest"),
            prediction=prediction_text,
            probability=probability_percent,
            amount=amount,
            risk_level=risk_level,
        )

        with open(pdf_file, "rb") as file:

            st.download_button(
                label="📄 Download Prediction Report",
                data=file,
                file_name="SecurePay_AI_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    except Exception as e:

        st.error(f"Error generating PDF: {e}")

    st.balloons()
