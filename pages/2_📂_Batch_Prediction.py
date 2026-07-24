import uuid

from utils.auth_guard import require_login
from database.db import get_connection
from reports.pdf_generator import generate_batch_report
import streamlit as st
import pandas as pd

from config import setup_page, load_css
from utils.ai_assistant import render_ai_assistant, render_batch_ai_assessment
from utils.model_loader import load_model, load_scaler

# --------------------------------------------------
# Page Configuration
# --------------------------------------------------

setup_page()
load_css()
require_login()
render_ai_assistant("batch")

st.markdown("""
<div class="hero-panel">
    <div class="hero-kicker">Bulk Fraud Screening</div>
    <div class="hero-title">Batch Transaction Review</div>
    <p class="hero-copy">
        Upload a transaction CSV, score every payment, identify the riskiest
        cases, and export reports for operational follow-up.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# --------------------------------------------------
# Load Model
# --------------------------------------------------

model = load_model()
scaler = load_scaler()

# --------------------------------------------------
# Upload CSV
# --------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload CSV",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    # --------------------------------------------------
    # Validate Columns
    # --------------------------------------------------

    expected_columns = [
        "Time",
        "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9",
        "V10", "V11", "V12", "V13", "V14", "V15", "V16", "V17",
        "V18", "V19", "V20", "V21", "V22", "V23", "V24",
        "V25", "V26", "V27", "V28",
        "Amount"
    ]

    # Remove the target column if it exists
    if "Class" in df.columns:
        df = df.drop(columns=["Class"])

    # Check for missing columns
    missing_columns = [col for col in expected_columns if col not in df.columns]

    if missing_columns:
        st.error(f"❌ Missing required columns: {missing_columns}")
        st.stop()

    # Reorder columns to exactly match the model
    df = df[expected_columns]
    # Verify the dataset has exactly 30 features

    if df.shape[1] != 30:
        st.error("❌ Expected exactly 30 input features.")
        st.stop()


    # Convert all values to numeric
    df = df.apply(pd.to_numeric, errors="coerce")

    # Check for invalid or missing values
    if df.isnull().values.any():
        st.error("❌ The uploaded CSV contains invalid or missing values.")
        st.stop()

    # --------------------------------------------------
    # Predict Button
    # --------------------------------------------------

    if st.button("🚀 Predict All", use_container_width=True):

        with st.spinner("🔍 Running AI Fraud Detection..."):

            # Scale Data
            scaled = scaler.transform(df)

            # Make Predictions
            predictions = model.predict(scaled)
            probabilities = model.predict_proba(scaled)[:, 1]

            # Create Results DataFrame
            results = df.copy()
            results["Prediction"] = predictions
            results["Fraud Probability"] = probabilities

            # Calculate Statistics
            fraud = (predictions == 1).sum()
            genuine = (predictions == 0).sum()

            total_transactions = len(results)
            fraud_transactions = int(fraud)
            genuine_transactions = int(genuine)
            fraud_rate = round((fraud / total_transactions) * 100, 2)

            # Save Batch History
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO batch_predictions
                (
                    username,
                    filename,
                    total,
                    fraud,
                    genuine,
                    fraud_rate
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    st.session_state.get("username","Guest"),
                    uploaded_file.name,
                    total_transactions,
                    fraud_transactions,
                    genuine_transactions,
                    fraud_rate,
                ),
            )

            conn.commit()
            conn.close()
            st.success("✅ Batch Prediction Completed!")



            #   Show summary
            c1, c2, c3 = st.columns(3)

            c1.metric("Total Transactions", total_transactions)
            c2.metric("Fraud", fraud_transactions)
            c3.metric("Genuine", genuine_transactions)

            st.metric("Fraud Rate", f"{fraud_rate}%")

            st.divider()

            render_batch_ai_assessment(
                total=total_transactions,
                fraud=fraud_transactions,
                genuine=genuine_transactions,
                fraud_rate=fraud_rate,
            )

            st.divider()

            # Show prediction results
            st.subheader("Prediction Results")
            st.dataframe(results, use_container_width=True)

            # Download CSV
            csv = results.to_csv(index=False).encode("utf-8")

            st.download_button(
                "📥 Download Results CSV",
                data=csv,
                file_name="batch_predictions.csv",
                mime="text/csv",
                use_container_width=True,
            )


            # Generate PDF
            try:
                pdf_file = generate_batch_report(
                    username=st.session_state.get("username", "Guest"),
                    df=results,
                )


                with open(pdf_file, "rb") as f:
                    st.download_button(
                        "📄 Download PDF Report",
                        data=f,
                        file_name="Batch_Report.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )

            except Exception as e:
             
              st.error(f"PDF Error: {e}")
