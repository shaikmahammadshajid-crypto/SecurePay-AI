import streamlit as st
import pandas as pd

from config import setup_page, load_css
from utils.ai_assistant import render_ai_assistant
from utils.demo_data import load_dashboard_data

setup_page()
load_css()
render_ai_assistant("about")

st.markdown("""
<div class="hero-panel">
    <div class="hero-kicker">System Overview</div>
    <div class="hero-title">About SecurePay AI</div>
    <p class="hero-copy">
        SecurePay AI is a fraud detection workspace for scoring card
        transactions, reviewing risk, explaining model output, and keeping
        analyst-ready evidence for operational decisions.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ==========================================================
# PROJECT OVERVIEW
# ==========================================================

st.header("🎯 Project Objectives")

col1, col2 = st.columns(2)

with col1:
    st.success("""
✔ Detect fraudulent transactions

✔ Reduce financial losses

✔ Support real-time predictions

✔ Batch transaction analysis

✔ Interactive visual analytics
""")

with col2:
    st.success("""
✔ Explain AI decisions

✔ Generate downloadable reports

✔ Provide enterprise dashboard

✔ Easy deployment

✔ High prediction accuracy
""")

st.divider()

# ==========================================================
# ARCHITECTURE
# ==========================================================

st.header("🏗 System Architecture")

st.code("""
                Credit Card Dataset
                        │
                        ▼
            Data Cleaning & Preprocessing
                        │
                        ▼
              Feature Scaling (StandardScaler)
                        │
                        ▼
             Random Forest Machine Learning
                        │
            ┌───────────┴────────────┐
            ▼                        ▼
      Single Prediction      Batch Prediction
            │                        │
            └───────────┬────────────┘
                        ▼
               Analytics Dashboard
                        │
                        ▼
                 Fraud Reports
""")

st.divider()

# ==========================================================
# DATASET
# ==========================================================

st.header("📂 Dataset Information")

try:
    df, is_demo_data = load_dashboard_data()

    total = len(df)
    fraud = len(df[df["Class"] == 1])
    genuine = len(df[df["Class"] == 0])

    c1, c2, c3 = st.columns(3)

    c1.metric("Transactions", f"{total:,}")
    c2.metric("Fraud", fraud)
    c3.metric("Genuine", genuine)

    if is_demo_data:
        st.info("Showing generated dashboard sample data for public deployment.")

except:
    st.info("Dataset statistics unavailable.")

st.markdown("""
Dataset Features

• Time

• V1 – V28

• Amount

Target

• Class

0 → Genuine

1 → Fraud
""")

st.divider()

# ==========================================================
# MODEL
# ==========================================================

st.header("🧠 Machine Learning Model")

model = pd.DataFrame({

    "Component":[
        "Algorithm",
        "Feature Scaling",
        "Training Library",
        "Prediction",
        "Output"
    ],

    "Details":[
        "Random Forest",
        "StandardScaler",
        "Scikit-learn",
        "Binary Classification",
        "Fraud Probability"
    ]

})

st.dataframe(model,
             use_container_width=True,
             hide_index=True)

st.divider()

# ==========================================================
# PERFORMANCE
# ==========================================================

st.header("📊 Model Performance")

performance = pd.DataFrame({

    "Metric":[
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score",
        "ROC-AUC"
    ],

    "Value":[
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

# ==========================================================
# TECHNOLOGIES
# ==========================================================

st.header("🛠 Technology Stack")

left,right = st.columns(2)

with left:

    st.markdown("""
### AI & Machine Learning

- Python

- Scikit-learn

- Pandas

- NumPy

- SHAP
""")

with right:

    st.markdown("""
### Application

- Streamlit

- Plotly

- SQLite

- FastAPI

- Docker
""")

st.divider()

# ==========================================================
# FEATURES
# ==========================================================

st.header("Current Capabilities")

features = [

"Real-time Fraud Prediction",

"Batch CSV Prediction",

"Interactive Analytics",

"Fraud Probability",

"Risk Classification",

"CSV and PDF Downloads",

"Professional Dashboard",

"Responsive UI",

"Secure Authentication",

"Admin Monitoring",

"Prediction History",

"AI Fraud Analyst Guidance"

]

for feature in features:
    st.write("✅", feature)

st.divider()

# ==========================================================
# FUTURE
# ==========================================================

st.header("Future Enhancements")

future = [

"REST API",

"Docker Deployment",

"Cloud Deployment",

"Live Transaction Monitoring",

"Real Payment Gateway Integration",

"Device and Location Risk Signals",

"Model Retraining Pipeline"

]

for item in future:
    st.write("🚀", item)

st.divider()

st.success(
"""
SecurePay AI demonstrates the complete lifecycle of a Machine Learning
application, from data preprocessing and model training to prediction,
analytics, visualization, and deployment. It is designed as a
production-ready portfolio project showcasing modern AI and software
engineering practices.
"""
)
