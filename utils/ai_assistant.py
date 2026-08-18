import streamlit as st

from database.admin import get_dashboard_stats
from database.history import get_user_history
from utils.app_health import get_app_health, health_summary
from utils.helpers import get_prediction_text, get_risk_level, probability_to_percentage
from utils.model_loader import load_model, load_scaler
from utils.prediction import predict_transaction


PAGE_LINKS = {
    "dashboard": ("Dashboard", "app.py"),
    "predict": ("Predict", "pages/1_💳_Predict.py"),
    "batch": ("Batch Prediction", "pages/2_📂_Batch_Prediction.py"),
    "analytics": ("Analytics", "pages/3_📊_Analytics.py"),
    "history": ("History", "pages/5_📜_History.py"),
    "profile": ("Profile", "pages/6_👤_Profile.py"),
    "admin": ("Admin", "pages/7_Admin.py"),
    "assistant": ("AI Assistant", "pages/8_🤖_AI_Assistant.py"),
}


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
    "assistant": {
        "intro": "Personalized command center for app navigation, reports, health checks, and risk summaries.",
        "quick": [
            "Summarize my activity",
            "Generate my audit report",
            "Check app health",
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

    if "do it" in text or "by itself" in text or "automatic" in text or "agent" in text:
        return (
            "I can guide and prepare app actions, open the right workspace, summarize your data, and recommend next "
            "steps. For security, actions that change accounts, create reports, or affect payment decisions should "
            "stay user-confirmed instead of running silently."
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


def summarize_user_history(username):
    rows = get_user_history(username)
    total = len(rows)

    if total == 0:
        return {
            "total": 0,
            "fraud": 0,
            "genuine": 0,
            "average_probability": 0.0,
            "latest": "No saved predictions yet.",
        }

    fraud = sum(1 for row in rows if "Fraud" in row["prediction"])
    average_probability = sum(float(row["probability"] or 0) for row in rows) / total
    latest_row = rows[0]

    return {
        "total": total,
        "fraud": fraud,
        "genuine": total - fraud,
        "average_probability": round(average_probability, 2),
        "latest": (
            f"{latest_row['transaction_id']} was {latest_row['prediction']} "
            f"at {latest_row['probability']}% probability."
        ),
    }


def detect_app_intent(prompt):
    text = prompt.lower().strip()

    if not text:
        return None

    if any(keyword in text for keyword in ["health", "status", "system check", "check app", "diagnose"]):
        return {"type": "health_check"}

    if any(keyword in text for keyword in ["audit report", "history report", "generate report", "create report", "pdf"]):
        return {"type": "history_report"}

    if any(keyword in text for keyword in ["admin summary", "admin stats", "platform summary"]):
        return {"type": "admin_summary"}

    if any(keyword in text for keyword in ["test model", "sample prediction", "demo prediction", "smoke test"]):
        return {"type": "model_smoke_test"}

    if any(keyword in text for keyword in ["summarize", "summary", "my activity", "risk summary", "highest risk"]):
        return {"type": "history_summary"}

    page_keywords = {
        "batch": ["batch", "csv", "upload", "bulk"],
        "predict": ["predict", "score", "single transaction", "payment"],
        "analytics": ["analytics", "chart", "dashboard data", "trend"],
        "history": ["history", "past", "audit", "download history"],
        "profile": ["profile", "account", "my stats"],
        "admin": ["admin", "users", "logs"],
        "dashboard": ["home", "dashboard", "overview"],
    }

    for page, keywords in page_keywords.items():
        if any(keyword in text for keyword in keywords):
            return {"type": "navigate", "page": page}

    return {"type": "answer", "answer": get_assistant_answer(prompt)}


def render_health_check(username):
    checks = get_app_health(username=username)
    summary = health_summary(checks)

    if summary["status"] == "ok":
        st.success(f"App health: {summary['message']}")
    else:
        st.warning(f"App health: {summary['message']}")

    for check in checks:
        if check["ok"]:
            st.write(f"OK: {check['name']} - {check['detail']}")
        else:
            st.write(f"Needs attention: {check['name']} - {check['detail']}")


def render_history_summary(username):
    if not username:
        st.warning("Login is required before I can summarize account activity.")
        return

    summary = summarize_user_history(username)
    st.info(
        f"Saved predictions: {summary['total']} | Fraud: {summary['fraud']} | "
        f"Genuine: {summary['genuine']} | Avg probability: {summary['average_probability']}%."
    )
    st.caption(summary["latest"])

    if summary["fraud"] > 0:
        st.warning("Priority: review fraud-labeled transactions first and export an audit report.")
    elif summary["total"] > 0:
        st.success("No fraud-labeled saved predictions for this account.")


def render_history_report(username):
    if not username:
        st.warning("Login is required before I can create an audit report.")
        return

    rows = get_user_history(username)
    if not rows:
        st.info("No prediction history is available for an audit report.")
        return

    summary = summarize_user_history(username)
    try:
        from reports.pdf_generator import generate_history_report

        pdf_file = generate_history_report(username=username, rows=rows, summary=summary)
    except ModuleNotFoundError as e:
        st.error(f"PDF generation dependency is missing: {e.name}")
        return

    with open(pdf_file, "rb") as file:
        st.download_button(
            "Download Audit Report",
            data=file,
            file_name="SecurePay_AI_Audit_Report.pdf",
            mime="application/pdf",
            use_container_width=True,
            key=f"audit_report_download_{username}",
        )


def render_admin_summary(role):
    if role != "admin":
        st.warning("Admin summary requires an administrator account.")
        return

    stats = get_dashboard_stats()
    c1, c2 = st.columns(2)
    c1.metric("Users", stats["users"])
    c2.metric("Predictions", stats["predictions"])
    c1.metric("Frauds", stats["frauds"])
    c2.metric("Batch Jobs", stats["batches"])


def render_model_smoke_test():
    try:
        model = load_model()
        scaler = load_scaler()
        prediction, probability = predict_transaction(model, scaler, [0.0] * 29 + [100.0])
    except Exception as e:
        st.error(f"Model test failed: {e}")
        return

    prediction_text = get_prediction_text(prediction)
    risk_level = get_risk_level(probability)
    probability_percent = probability_to_percentage(probability)

    st.success("Model test completed.")
    st.write(f"Sample result: {prediction_text}")
    st.write(f"Fraud probability: {probability_percent}%")
    st.write(f"Risk level: {risk_level}")


def render_agent_result(prompt, current_page=None):
    intent = detect_app_intent(prompt)

    if intent is None:
        st.info("Tell me what you want to do in SecurePay AI.")
        return

    if intent["type"] == "navigate":
        page = intent["page"]
        label, path = PAGE_LINKS[page]
        if page == "admin" and st.session_state.get("role") != "admin":
            st.warning("Admin actions require an administrator account.")
        elif page == current_page:
            st.info(f"You are already in {label}.")
        else:
            st.switch_page(path)
        return

    if intent["type"] == "health_check":
        render_health_check(st.session_state.get("username"))
        return

    if intent["type"] == "history_report":
        render_history_report(st.session_state.get("username"))
        return

    if intent["type"] == "admin_summary":
        render_admin_summary(st.session_state.get("role"))
        return

    if intent["type"] == "history_summary":
        render_history_summary(st.session_state.get("username"))
        return

    if intent["type"] == "model_smoke_test":
        render_model_smoke_test()
        return

    st.write(intent["answer"])


def render_ai_assistant(page_key):
    guide = PAGE_GUIDES.get(page_key, PAGE_GUIDES["dashboard"])

    with st.sidebar:
        st.markdown("### Personalized AI Assistant")
        st.caption(guide["intro"])

        quick_prompt = st.selectbox(
            "Quick help",
            ["Ask a custom question"] + guide["quick"],
            key=f"{page_key}_assistant_quick",
        )

        custom_prompt = st.text_area(
            "Ask or request an app action",
            placeholder="Example: open batch prediction, summarize my activity, explain high risk",
            key=f"{page_key}_assistant_prompt",
            height=92,
        )

        prompt = custom_prompt.strip()
        if not prompt and quick_prompt != "Ask a custom question":
            prompt = quick_prompt

        if st.button("Run Assistant", key=f"{page_key}_assistant_run", use_container_width=True):
            render_agent_result(prompt, current_page=page_key)

        st.markdown(
            '<div class="assistant-note">The assistant can navigate, summarize, and advise. '
            'Sensitive changes remain user-confirmed.</div>',
            unsafe_allow_html=True,
        )


def render_ai_workspace():
    st.markdown("""
<div class="hero-panel">
    <div class="hero-kicker">Personalized AI Operations</div>
    <div class="hero-title">AI Assistant</div>
    <p class="hero-copy">
        Run app-aware commands, inspect system readiness, summarize account risk,
        and generate audit-ready evidence from your saved activity.
    </p>
</div>
""", unsafe_allow_html=True)

    st.divider()

    prompt = st.text_area(
        "Command",
        placeholder="Examples: check app health, summarize my activity, generate my audit report, open batch prediction",
        height=110,
        key="assistant_workspace_prompt",
    )

    col1, col2, col3, col4 = st.columns(4)

    quick_prompt = None

    if col1.button("Health", use_container_width=True):
        quick_prompt = "check app health"
    if col2.button("Summary", use_container_width=True):
        quick_prompt = "summarize my activity"
    if col3.button("Report", use_container_width=True):
        quick_prompt = "generate my audit report"
    if col4.button("Model Test", use_container_width=True):
        quick_prompt = "test model"

    if quick_prompt or st.button("Execute", use_container_width=True):
        render_agent_result(quick_prompt or prompt, current_page="assistant")
