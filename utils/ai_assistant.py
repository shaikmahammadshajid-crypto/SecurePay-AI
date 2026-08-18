from database.admin import get_dashboard_stats
from database.history import get_user_history


PAGE_LINKS = {
    "dashboard": "dashboard",
    "predict": "predict",
    "batch": "batch",
    "analytics": "analytics",
    "history": "history",
    "profile": "profile",
    "admin": "admin",
    "assistant": "assistant",
}


ANSWERS = {
    "can't i login after registration": (
        "After registration the app signs you in automatically. Usernames are saved in lowercase, "
        "so login is case-insensitive. Use the same password you entered during registration."
    ),
    "cant i login after registration": (
        "After registration the app signs you in automatically. Usernames are saved in lowercase, "
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
        "Use Predict for one transaction, Batch for CSV screening, Analytics for labeled datasets, "
        "and History or Reports for audit review."
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
        "Use distributions to compare fraud and genuine behavior, amount metrics to identify unusual "
        "transaction sizes, and top-fraud rows to inspect extreme examples."
    ),
    "saved": "Single predictions are saved in the local SQLite prediction_history table for the logged-in user.",
    "export": "Use CSV downloads on batch results and PDF audit reports from Assistant or History.",
    "history empty": "History is empty until the current user completes a single transaction prediction.",
    "profile show": "Profile shows account details, total predictions, fraud count, genuine count, and recent history.",
    "fraud count": "Fraud count is calculated from saved predictions marked as Fraud Transaction.",
    "model work": (
        "The app scales 30 transaction features and sends them to a Random Forest classifier that returns a "
        "fraud/genuine class and probability."
    ),
    "v1 to v28": "V1 to V28 are anonymized PCA-transformed transaction features from the source dataset.",
    "what makes this ai-based": (
        "The project uses a trained machine-learning model for fraud scoring, probability-based risk decisions, "
        "batch inference, analytics, and AI-style operational recommendations."
    ),
    "admins see": "Admins can see users, prediction logs, fraud counts, batch jobs, and downloadable summaries.",
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
            "username is typed without spaces. New registrations log in automatically."
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
            "I can run safe app actions such as navigation, health checks, activity summaries, model tests, and "
            "audit report generation. Payment decisions and account changes stay user-confirmed."
        )

    return (
        "I could not match that exactly. Try asking about fraud probability, high-risk actions, CSV columns, "
        "registration login, reports, app health, model tests, or admin monitoring."
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


def get_batch_assessment(total, fraud, genuine, fraud_rate):
    if fraud_rate >= 10:
        action = "Critical batch anomaly. Pause downstream settlement and review the upload source."
    elif fraud_rate >= 2:
        action = "Elevated fraud concentration. Prioritize the highest probability rows for manual review."
    elif fraud > 0:
        action = "Fraud detected. Export the report and investigate the flagged transactions first."
    else:
        action = "No fraud flagged. Keep the report as an audit record and continue monitoring."

    return {
        "summary": f"Screened {total:,} transactions: {fraud:,} fraud and {genuine:,} genuine.",
        "action": action,
        "fraud_rate": fraud_rate,
    }


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
        "assistant": ["assistant", "agent", "ai command"],
    }

    for page, keywords in page_keywords.items():
        if any(keyword in text for keyword in keywords):
            return {"type": "navigate", "page": page}

    return {"type": "answer", "answer": get_assistant_answer(prompt)}
