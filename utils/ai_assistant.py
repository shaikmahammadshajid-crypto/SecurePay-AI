import streamlit as st


PAGE_GUIDES = {
    "login": {
        "intro": "Use Login for an existing account or Register to create one.",
        "quick": [
            "How do I login?",
            "How do I create an account?",
            "What is the admin account?",
        ],
    },
    "dashboard": {
        "intro": "Review model metrics, quick navigation, dataset summary, and live fraud charts.",
        "quick": [
            "Where should I start?",
            "What does fraud probability mean?",
            "How do I download reports?",
        ],
    },
    "predict": {
        "intro": "Enter Time, Amount, and V1 to V28 values to score one transaction.",
        "quick": [
            "What values do I enter?",
            "How should I interpret the risk level?",
            "Why are V1 to V28 hidden names?",
        ],
    },
    "batch": {
        "intro": "Upload a CSV with Time, V1 to V28, and Amount columns to score many transactions.",
        "quick": [
            "What CSV columns are required?",
            "Can the CSV include Class?",
            "What can I download after prediction?",
        ],
    },
    "analytics": {
        "intro": "Upload a labeled dataset with a Class column to explore fraud trends and distributions.",
        "quick": [
            "What does Class mean?",
            "How do I read the charts?",
            "Why is fraud rate so low?",
        ],
    },
    "history": {
        "intro": "Review and export your previous single transaction predictions.",
        "quick": [
            "Where are predictions saved?",
            "How do I export my history?",
            "Why is my history empty?",
        ],
    },
    "profile": {
        "intro": "See your account details and a summary of your prediction activity.",
        "quick": [
            "What does my profile show?",
            "How is fraud count calculated?",
            "Why is history empty?",
        ],
    },
    "about": {
        "intro": "Learn how SecurePay AI works, what dataset it uses, and what the model outputs.",
        "quick": [
            "How does the model work?",
            "What are V1 to V28?",
            "What technology is used?",
        ],
    },
    "admin": {
        "intro": "Monitor users, prediction logs, fraud counts, and batch jobs.",
        "quick": [
            "What can admins see?",
            "How are prediction logs counted?",
            "How do I export admin data?",
        ],
    },
}


ANSWERS = {
    "login": "Enter your username and password, then press Login. If you do not have an account, use the Register tab first.",
    "create account": "Open the Register tab, enter a username, email, and password, then submit. The password is stored as a bcrypt hash.",
    "admin account": "The default admin account is created automatically if missing. Username: admin. Password: admin123.",
    "start": "Start with Predict for one transaction, Batch Prediction for a CSV file, or Analytics if you want to inspect a labeled dataset.",
    "fraud probability": "Fraud probability is the model's estimated chance that the transaction is fraudulent. Higher values require stronger review or blocking action.",
    "download reports": "Prediction and Batch pages provide download buttons after a successful prediction. History and Admin pages can export CSV logs.",
    "values": "Use the same feature format as the credit card fraud dataset: Time, V1 through V28, and Amount. V1 to V28 are anonymized PCA features.",
    "risk level": "Risk levels are based on fraud probability: low values are usually approved, medium values need monitoring, and high values need verification or blocking.",
    "v1": "V1 to V28 are anonymized numeric features produced from the original transaction fields to protect sensitive cardholder information.",
    "csv columns": "A batch CSV must contain Time, V1, V2, ..., V28, and Amount. The app reorders these columns before prediction.",
    "class": "Class is the real label in the dataset: 0 means genuine and 1 means fraud. Batch prediction can remove it before scoring; Analytics needs it for charts.",
    "download after prediction": "After batch prediction, you can download the scored CSV and a PDF batch report.",
    "charts": "Pie and bar charts compare fraud versus genuine transactions. Histograms show amount patterns. The heatmap shows feature correlations.",
    "fraud rate": "Credit card fraud datasets are highly imbalanced, so fraud is normally a very small percentage of total transactions.",
    "saved": "Single predictions are saved in the local SQLite prediction history table for the logged-in user.",
    "export": "Use the Download CSV button on History or Admin pages to export the visible records.",
    "history empty": "History is empty when the current user has not completed any single transaction predictions yet.",
    "profile show": "The profile page shows account details, total predictions, fraud count, genuine count, and recent history.",
    "fraud count": "Fraud count is calculated from saved predictions marked as Fraud Transaction.",
    "model work": "The app scales the 30 transaction features and sends them to a trained Random Forest classifier, which returns a class and probability.",
    "technology": "The app uses Streamlit, Python, pandas, scikit-learn, Plotly, SQLite, bcrypt, SHAP, and ReportLab.",
    "admins see": "Admins can see registered users, total prediction activity, fraud counts, batch jobs, and downloadable CSV logs.",
    "logs counted": "Admin prediction logs are counted from the saved prediction history table, and batch jobs are counted from batch prediction records.",
}


def get_assistant_answer(question):
    text = question.lower().strip()

    if not text:
        return "Ask about predictions, batch CSV format, analytics, risk levels, reports, login, profile, or admin features."

    for keyword, answer in ANSWERS.items():
        if keyword in text:
            return answer

    if "help" in text:
        return "I can help with login, single prediction, batch CSV upload, analytics, history, profile, admin logs, risk levels, and reports."

    return (
        "I could not match that exactly. Try asking about CSV columns, fraud probability, "
        "risk level, reports, login, history, analytics, or admin data."
    )


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
            placeholder="Example: What CSV columns are required?",
        )

        st.info(get_assistant_answer(question))
