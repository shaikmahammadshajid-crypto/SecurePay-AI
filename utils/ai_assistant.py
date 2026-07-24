import streamlit as st


PAGE_GUIDES = {
    "login": {
        "intro": "Account access, registration, and credential troubleshooting.",
        "quick": [
            "Why can't I login after registration?",
            "How do I create an account?",
            "What is the admin account?",
        ],
    },
    "dashboard": {
        "intro": "Operational overview for fraud monitoring and model usage.",
        "quick": [
            "Where should I start?",
            "How should fraud probability be used?",
            "What real-world workflow does this support?",
        ],
    },
    "predict": {
        "intro": "Single-transaction fraud triage and analyst recommendations.",
        "quick": [
            "What values do I enter?",
            "How do I interpret high risk?",
            "What should a bank do next?",
        ],
    },
    "batch": {
        "intro": "Bulk transaction screening, case prioritization, and report export.",
        "quick": [
            "What CSV columns are required?",
            "How should batch frauds be reviewed?",
            "Can the CSV include Class?",
        ],
    },
    "analytics": {
        "intro": "Dataset investigation, fraud imbalance, and monitoring insights.",
        "quick": [
            "What does Class mean?",
            "Why is fraud rate so low?",
            "How do I use the charts?",
        ],
    },
    "history": {
        "intro": "Audit trail for past predictions and user-level investigation.",
        "quick": [
            "Where are predictions saved?",
            "How do I export my history?",
            "Why is my history empty?",
        ],
    },
    "profile": {
        "intro": "Account activity, prediction totals, and personal usage summary.",
        "quick": [
            "What does my profile show?",
            "How is fraud count calculated?",
            "Why is history empty?",
        ],
    },
    "about": {
        "intro": "Model, dataset, architecture, and project explanation.",
        "quick": [
            "How does the model work?",
            "What are V1 to V28?",
            "What makes this AI-based?",
        ],
    },
    "admin": {
        "intro": "Admin monitoring for users, prediction logs, and batch jobs.",
        "quick": [
            "What can admins see?",
            "How are prediction logs counted?",
            "How should fraud operations use this?",
        ],
    },
}


ANSWERS = {
    "can't i login after registration": (
        "After registration the app now signs you in automatically. Usernames are saved in lowercase, "
        "so login is case-insensitive. Use the same password you entered during registration."
    ),
    "cant i login after registration": (
        "After registration the app now signs you in automatically. Usernames are saved in lowercase, "
        "so login is case-insensitive. Use the same password you entered during registration."
    ),
    "create an account": (
        "Open Register, enter a unique username, unique email, and a password with at least 6 characters. "
        "The password is stored only as a bcrypt hash."
    ),
    "admin account": (
        "Admin access is configured by the deployment owner. Set SECUREPAY_ADMIN_PASSWORD "
        "before first run to create an admin account."
    ),
    "where should i start": (
        "Use Predict for one transaction, Batch Prediction for a CSV screening job, and Analytics for "
        "understanding labeled fraud patterns."
    ),
    "fraud probability": (
        "Fraud probability is a decision-support score. Low scores can usually be approved, medium scores "
        "should be monitored, and high scores should trigger verification or blocking."
    ),
    "real-world workflow": (
        "A realistic workflow is score transaction, classify risk, save audit history, review high-risk cases, "
        "export evidence, and let admins monitor user and fraud activity."
    ),
    "values do i enter": (
        "Enter Time, Amount, and V1 through V28 in the same format as the credit card fraud dataset. "
        "V1 to V28 are anonymized PCA features."
    ),
    "high risk": (
        "High risk should trigger stronger controls: step-up authentication, customer contact, transaction hold, "
        "manual review, and account monitoring."
    ),
    "bank do next": (
        "A bank should combine the model result with business rules, customer history, device/IP signals, and "
        "manual review before final action."
    ),
    "csv columns": "Batch CSV requires Time, V1 to V28, and Amount. If Class exists, the app removes it before scoring.",
    "batch frauds": (
        "Sort by fraud probability, review the highest-risk transactions first, export the report, and escalate "
        "critical cases to the fraud operations team."
    ),
    "class": "Class is the ground-truth label in the dataset: 0 means genuine and 1 means fraud.",
    "fraud rate": (
        "Fraud is rare, so real datasets are heavily imbalanced. Accuracy alone can look high even when fraud "
        "recall is poor, so probability, recall, and analyst review matter."
    ),
    "charts": (
        "Use distribution charts to compare fraud and genuine behavior, amount histograms to identify unusual "
        "transaction sizes, and correlation to inspect feature relationships."
    ),
    "saved": "Single predictions are saved in the local SQLite prediction_history table for the logged-in user.",
    "export": "Use the CSV or PDF download buttons on prediction, batch, history, and admin pages.",
    "history empty": "History is empty until the current user completes a single transaction prediction.",
    "profile show": "Profile shows account details, total predictions, fraud count, genuine count, and recent history.",
    "fraud count": "Fraud count is calculated from saved predictions marked as Fraud Transaction.",
    "model work": (
        "The app scales 30 transaction features and sends them to a Random Forest classifier that returns a "
        "fraud/genuine class and probability."
    ),
    "v1 to v28": "V1 to V28 are anonymized PCA-transformed transaction features from the source dataset.",
    "what makes this ai-based": (
        "The project uses a trained machine-learning model for fraud scoring, SHAP explainability, probability-based "
        "risk decisions, batch inference, analytics, and AI-style operational recommendations."
    ),
    "admins see": "Admins can see users, prediction logs, fraud counts, batch jobs, and downloadable CSV reports.",
    "logs counted": "Prediction logs are counted from prediction_history; batch jobs are counted from batch_predictions.",
    "fraud operations": (
        "Fraud teams can use this as a triage console: detect, prioritize, investigate, export reports, and monitor "
        "operational activity."
    ),
}


def get_assistant_answer(question):
    text = question.lower().strip()

    if not text:
        return (
            "Ask about login, transaction scoring, fraud probability, batch CSVs, analytics, reports, "
            "admin monitoring, or real-world fraud workflows."
        )

    for keyword, answer in ANSWERS.items():
        if keyword in text:
            return answer

    if "login" in text or "credential" in text or "password" in text:
        return (
            "Check that the account exists, the password has the exact characters used at registration, and the "
            "username is typed without spaces. New registrations now log in automatically."
        )

    if "approve" in text or "block" in text or "review" in text:
        return (
            "Use probability as a triage signal: approve low-risk payments, monitor medium-risk payments, request "
            "verification for high-risk payments, and block or hold critical-risk payments."
        )

    if "help" in text:
        return (
            "I can help with account access, single prediction, batch prediction, analytics, history, profile, "
            "admin review, reports, and fraud response decisions."
        )

    return (
        "I could not match that exactly. Try asking about fraud probability, high-risk actions, CSV columns, "
        "registration login, SHAP explanation, reports, or admin monitoring."
    )


def get_transaction_assessment(prediction, probability, amount, risk_level):
    if probability >= 0.85:
        action = "Block or hold the transaction immediately."
        review = "Escalate to fraud operations and contact the customer through a trusted channel."
    elif probability >= 0.60:
        action = "Request step-up verification before approval."
        review = "Review recent account activity, transaction velocity, and device/location signals."
    elif probability >= 0.30:
        action = "Allow only with monitoring or lightweight verification."
        review = "Compare against the customer's normal amount range and merchant behavior."
    else:
        action = "Approve under normal controls."
        review = "Keep the result in history for audit and future pattern monitoring."

    return {
        "decision": "Fraud review required" if prediction == 1 else "Likely genuine",
        "action": action,
        "review": review,
        "summary": (
            f"Amount ${amount:,.2f} is classified as {risk_level} with "
            f"{probability * 100:.2f}% fraud probability."
        ),
    }


def render_transaction_ai_assessment(prediction, probability, amount, risk_level):
    assessment = get_transaction_assessment(
        prediction=prediction,
        probability=probability,
        amount=amount,
        risk_level=risk_level,
    )

    st.subheader("AI Fraud Analyst")
    c1, c2 = st.columns(2)

    with c1:
        st.info(f"Decision Support: {assessment['decision']}")
        st.write(assessment["summary"])

    with c2:
        st.warning(assessment["action"])
        st.write(assessment["review"])


def render_batch_ai_assessment(total, fraud, genuine, fraud_rate):
    st.subheader("AI Batch Investigation Summary")

    if fraud_rate >= 10:
        action = "Critical batch anomaly. Pause downstream settlement and review the upload source."
    elif fraud_rate >= 2:
        action = "Elevated fraud concentration. Prioritize the highest probability rows for manual review."
    elif fraud > 0:
        action = "Fraud detected. Export the report and investigate the flagged transactions first."
    else:
        action = "No fraud flagged. Keep the report as an audit record and continue monitoring."

    c1, c2 = st.columns(2)
    with c1:
        st.info(
            f"Screened {total:,} transactions: {fraud:,} fraud and {genuine:,} genuine."
        )
    with c2:
        st.warning(f"{action} Fraud rate: {fraud_rate:.2f}%.")


def render_ai_assistant(page_key):
    guide = PAGE_GUIDES.get(page_key, PAGE_GUIDES["dashboard"])
    state_key = f"assistant_question_{page_key}"

    with st.sidebar:
        st.divider()
        st.markdown("### AI Assistant")
        st.caption(guide["intro"])

        selected = st.selectbox(
            "Quick help",
            ["Ask a question"] + guide["quick"],
            key=f"assistant_quick_{page_key}",
        )

        if selected != "Ask a question":
            st.session_state[state_key] = selected

        question = st.text_input(
            "Ask SecurePay AI",
            key=state_key,
            placeholder="Example: What should a bank do next?",
        )

        st.info(get_assistant_answer(question))
