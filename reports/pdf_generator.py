import os
from xml.sax.saxutils import escape

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


def _safe_text(value):
    text = str(value)
    text = text.encode("ascii", "ignore").decode("ascii")
    return escape(text)


def _safe_filename(value):
    text = str(value).strip().lower()
    safe = "".join(char if char.isalnum() or char in ("-", "_") else "_" for char in text)
    return safe or "securepay_user"


def generate_prediction_report(
        username,
        prediction,
        probability,
        amount,
        risk_level):

    os.makedirs("reports/generated", exist_ok=True)

    filename = f"reports/generated/{_safe_filename(username)}_report.pdf"

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b>SecurePay AI</b>", styles["Title"])
    )

    elements.append(
        Paragraph("Credit Card Fraud Detection Report",
                  styles["Heading2"])
    )

    elements.append(
        Paragraph("<br/>", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>User:</b> {_safe_text(username)}",
                  styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Prediction:</b> {_safe_text(prediction)}",
                  styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Fraud Probability:</b> {probability:.2f}%",
                  styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Amount:</b> ${amount}",
                  styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Risk Level:</b> {_safe_text(risk_level)}",
                  styles["BodyText"])
    )

    doc.build(elements)

    return filename

# -------------------------------
# Batch Prediction PDF Report
# -------------------------------
def generate_batch_report(df, username):
    """
    Generate PDF report for batch prediction results.
    """

    os.makedirs("reports/generated", exist_ok=True)

    filename = f"reports/generated/{_safe_filename(username)}_batch_report.pdf"

    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("<b>SecurePay AI</b>", styles["Title"])
    )

    elements.append(
        Paragraph("Batch Prediction Report", styles["Heading2"])
    )

    elements.append(
        Paragraph("<br/>", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>User:</b> {_safe_text(username)}", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Total Transactions:</b> {len(df)}", styles["BodyText"])
    )

    # Count fraud and genuine transactions
    if df["Prediction"].dtype == object:
        fraud = (df["Prediction"] == "Fraud").sum()
        genuine = (df["Prediction"] == "Genuine").sum()
    else:
        fraud = (df["Prediction"] == 1).sum()
        genuine = (df["Prediction"] == 0).sum()

    elements.append(
        Paragraph(f"<b>Fraud Transactions:</b> {fraud}", styles["BodyText"])
    )

    elements.append(
        Paragraph(f"<b>Genuine Transactions:</b> {genuine}", styles["BodyText"])
    )

    doc.build(elements)

    return filename


def generate_history_report(username, rows, summary):
    os.makedirs("reports/generated", exist_ok=True)

    filename = f"reports/generated/{_safe_filename(username)}_audit_report.pdf"
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    elements = [
        Paragraph("<b>SecurePay AI</b>", styles["Title"]),
        Paragraph("Prediction Audit Report", styles["Heading2"]),
        Paragraph("<br/>", styles["BodyText"]),
        Paragraph(f"<b>User:</b> {_safe_text(username)}", styles["BodyText"]),
        Paragraph(f"<b>Total Predictions:</b> {summary['total']}", styles["BodyText"]),
        Paragraph(f"<b>Fraud Predictions:</b> {summary['fraud']}", styles["BodyText"]),
        Paragraph(f"<b>Genuine Predictions:</b> {summary['genuine']}", styles["BodyText"]),
        Paragraph(
            f"<b>Average Fraud Probability:</b> {summary['average_probability']:.2f}%",
            styles["BodyText"],
        ),
        Paragraph("<br/>", styles["BodyText"]),
        Paragraph("<b>Recent Predictions</b>", styles["Heading3"]),
    ]

    for row in rows[:10]:
        elements.append(
            Paragraph(
                " - ".join(
                    [
                        _safe_text(row["created_at"]),
                        _safe_text(row["transaction_id"]),
                        _safe_text(row["prediction"]),
                        f"{float(row['probability'] or 0):.2f}%",
                        f"${float(row['amount'] or 0):,.2f}",
                        _safe_text(row["risk_level"]),
                    ]
                ),
                styles["BodyText"],
            )
        )

    doc.build(elements)

    return filename


def generate_project_presentation_pdf():
    os.makedirs("reports/generated", exist_ok=True)

    filename = "reports/generated/SecurePayAI_Final_Project_Presentation.pdf"
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    slides = [
        (
            "SecurePay AI",
            [
                "AI-Powered Credit Card Fraud Detection System",
                "Final year machine learning web application",
                "Presented by Shaik Mahammad Shajid",
            ],
        ),
        (
            "Main Task",
            [
                "Detect potentially fraudulent credit card transactions using machine learning.",
                "Accept transaction features, predict genuine or fraud, calculate fraud probability, assign risk level, recommend action, and store the result for audit.",
            ],
        ),
        (
            "Problem Statement",
            [
                "Credit card fraud creates financial loss for customers, banks, and merchants.",
                "Fraud cases are rare, so accuracy alone can be misleading.",
                "A useful system must support review workflow, probability-based triage, and evidence storage.",
            ],
        ),
        (
            "Proposed Solution",
            [
                "Flask web app deployed on Render with Gunicorn.",
                "Random Forest model for transaction classification.",
                "SQLite audit history, authentication, batch screening, reports, admin dashboard, and AI Assistant.",
            ],
        ),
        (
            "Technology Stack",
            [
                "Backend and frontend: Flask templates with HTML/CSS.",
                "Machine learning: scikit-learn, Pandas, NumPy, Joblib.",
                "Database and security: SQLite and bcrypt.",
                "Deployment: Render Python service with /health endpoint.",
            ],
        ),
        (
            "Core Workflow",
            [
                "User logs in or opens public demo.",
                "Transaction features are validated and scaled.",
                "Random Forest predicts fraud probability.",
                "Risk level and recommendation are displayed.",
                "Prediction is saved for history, audit, and PDF reporting.",
            ],
        ),
        (
            "Features",
            [
                "Single prediction, batch CSV screening, prediction history, profile summary.",
                "AI Assistant commands: health check, activity summary, model test, report generation, and navigation.",
                "Admin dashboard for user and prediction monitoring.",
            ],
        ),
        (
            "Testing and Reliability",
            [
                "Pytest validates auth, model loading, prediction validation, assistant commands, Flask routes, and runtime config.",
                "Health endpoint verifies model artifact, scaler artifact, and SQLite database readiness.",
                "The project does not claim impossible 100 percent accuracy; model quality should be measured with precision, recall, F1, ROC-AUC, and confusion matrix.",
            ],
        ),
        (
            "Reviewer Demo Script",
            [
                "Open Public Demo to show the main task without login.",
                "Register or login, open Predict, use a demo transaction, and submit.",
                "Show risk result, history, AI Assistant health check, and presentation PDF download.",
            ],
        ),
        (
            "Conclusion",
            [
                "SecurePay AI is a complete fraud detection workflow, not only a prediction script.",
                "It combines machine learning, web deployment, security, audit history, reporting, AI assistance, and testing.",
            ],
        ),
    ]

    elements = []
    for index, (title, bullets) in enumerate(slides, start=1):
        elements.append(Paragraph(f"Slide {index}: {_safe_text(title)}", styles["Title"]))
        elements.append(Spacer(1, 12))
        for bullet in bullets:
            elements.append(Paragraph(f"- {_safe_text(bullet)}", styles["BodyText"]))
            elements.append(Spacer(1, 7))
        if index != len(slides):
            elements.append(PageBreak())

    doc.build(elements)

    return filename
